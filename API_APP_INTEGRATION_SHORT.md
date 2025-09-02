# ZeroLinkChain API – App Integration Short Guide
Version: 1.0.0 (Condensed)

## 1. Base Config
Production Base URL: https://zerolinkchain.com/api/
WebSocket: wss://zerolinkchain.com/ws

## 1.1 Open Access & Auth Models
The API is intentionally open for broad integration. Avoid shipping a static secret in distributed apps (it will be extracted). Use one of these patterns instead:

Auth Modes:
- Public (Unauthenticated) READ: Health (/health), network (/stats, /api/blockchain/network), discovery (limited) – safe to allow without key if rate-limited.
- Wallet Signature: Sign a deterministic payload (e.g. `METHOD|PATH|TIMESTAMP`) and send headers:
  - X-Wallet-Address
  - X-Wallet-Signature (hex/BASE64 signature)
- Ephemeral Session Token: Client signs a server-issued challenge once → server returns short-lived token (e.g. 5–15 min) used as `Authorization: Bearer <session>`.
- Optional API Key: Only for backend-to-backend; NEVER embed in mobile/web bundles.

Mitigations vs Key Leakage:
1. Prefer signature-based auth over static keys.
2. If a key must exist in client, scope it (read-only) + short TTL + rotate.
3. Enforce per-IP + per-wallet rate limiting.
4. Reject timestamps older than ±120s to reduce replay.
5. For transfers/mining submits: require signature even if a bearer key is present.

Recommended Header Precedence:
1. Wallet signature (strongest user-bound)
2. Ephemeral session token
3. API key (backend only)

Example Canonical String To Sign:
`GET|/api/wallet/balance|1735229000` → HMAC / ECDSA / Ed25519 over this string.

Server SHOULD return 401 with a challenge JSON if signature missing for protected write endpoints.

## 2. Core Flows (Concept)
A. Status: GET /stats for global snapshot.
B. Mining: work → solve → submit → stats. (Respect ≥10s between work fetches.)
C. Wallet: create/import → balance → transfer → history.
D. Proxy: discover → (optional route) → register/heartbeat (if provider) → hop accounting.
E. Blockchain: network meta → specific block.
F. Realtime: WebSocket subscribe to events.

## 2.1 Core Flows (cURL Examples)
Environment variable tip (Unix shells):
export ZLC_API="https://zerolinkchain.com/api"; export WALLET="miner001"

### A. Status & Health
```bash
# System stats (public read)
curl "$ZLC_API/stats"

# Health
curl "$ZLC_API/health"
```

### B. Mining Cycle
```bash
# 1. Get work
curl "$ZLC_API/api/mining/work?wallet=$WALLET"

# (Client computes PoW: find nonce & hash meeting target)

# 2. Submit work (example values)
curl -X POST -H 'Content-Type: application/json' \
  -d '{"wallet":"'$WALLET'","work_id":"ZLC_example_123","nonce":1234567,"hash":"000000abc..."}' \
  "$ZLC_API/api/mining/submit"

# 3. Mining stats
curl "$ZLC_API/api/mining/stats?wallet=$WALLET"
```

### C. Wallet Lifecycle
```bash
# Basic create (random address)
curl -X POST "$ZLC_API/v1/wallet/create"

# Create with mnemonic
curl -X POST "$ZLC_API/v1/wallet/mnemonic/create"

# Import mnemonic
curl -X POST -H 'Content-Type: application/json' \
  -d '{"mnemonic":"ability access agent alpha ..."}' \
  "$ZLC_API/v1/wallet/mnemonic/import"

# Import private key
curl -X POST -H 'Content-Type: application/json' \
  -d '{"privateKey":"deadbeefcafebabefeedface..."}' \
  "$ZLC_API/v1/wallet/privkey/import"

# Get balance (RLA)
curl "$ZLC_API/wallet/balance?wallet=$WALLET"

# Transfer
curl -X POST -H 'Content-Type: application/json' \
  -d '{"from":"sender_wallet","to":"receiver_wallet","amount":12.5}' \
  "$ZLC_API/wallet/transfer"

# History
curl "$ZLC_API/wallet/history?wallet=$WALLET&limit=10"
```

### D. Proxy / VPN
```bash
# Discover proxies
curl "$ZLC_API/api/proxy/discover?limit=10"

# Plan route (3 hops, min 10 Mbps)
curl "$ZLC_API/api/proxy/route?hops=3&min_bandwidth=10"

# Register proxy node
curl -X POST -H 'Content-Type: application/json' \
  -d '{"wallet":"provider_wallet","ip":"203.0.113.15","port":8080}' \
  "$ZLC_API/api/proxy/register"

# Heartbeat
curl -X POST -H 'Content-Type: application/json' -d '{"wallet":"provider_wallet"}' \
  "$ZLC_API/api/proxy/heartbeat"

# Record hop
curl -X POST -H 'Content-Type: application/json' \
  -d '{"provider_wallet":"provider_wallet","user_wallet":"user_wallet_123"}' \
  "$ZLC_API/api/proxy/hop"
```

Upcoming (CloudProx native):
```
# Draft endpoints (subject to change)
POST /v1/cloudprox/route            # body: { min_hops, min_bandwidth, required_protocol_flags }
GET  /v1/cloudprox/route/{id}       # route status / AEAD seq
GET  /v1/cloudprox/hosts            # sanitized host list
GET  /v1/cloudprox/metrics          # aggregate metrics
```

### E. Blockchain Data
```bash
# Network info
curl "$ZLC_API/api/blockchain/network"

# Specific block
curl "$ZLC_API/api/blockchain/block/100"
```

### F. Signature-Based Auth Example
Assume you build a signature over: METHOD|PATH|TIMESTAMP
```bash
TS=$(date +%s)
CANONICAL="GET|/api/wallet/balance|$TS"
SIG=$(printf "%s" "$CANONICAL" | openssl dgst -sha256 -hmac "$PRIVATE_KEY" -binary | openssl base64)
curl -H "X-Wallet-Address: $WALLET" \
     -H "X-Wallet-Signature: $SIG" \
     -H "X-Timestamp: $TS" \
     "$ZLC_API/wallet/balance?wallet=$WALLET"
```

### G. WebSocket (Example Using wscat)
```bash
wscat -c wss://zerolinkchain.com/ws
# Then send:
{"action":"subscribe","events":["blocks","mining","proxy_updates"]}
```

Notes:
- Rotate or avoid static API keys; prefer signatures.
- Cache immutable block responses.
- Respect rate limiting (sleep if HTTP 429 + retry headers).

## 3. Minimal Response Shapes
Mining Work:
{ work_id, wallet, target, difficulty, timestamp, status, algorithm }
Submit Result:
{ work_id, wallet, status: "accepted"|"rejected", reward?, reason? }
Balance:
{ wallet, balance, mining_rewards, proxy_fees, service_fees, blocks_mined, proxy_hops, active, created }
Proxy Discovery:
{ status, count, nodes: [{ id, ip, port, type, country, bandwidth_mbps, latency_ms, reliability, active }] }
Route:
{ route_id, hops, total_latency, min_bandwidth, asn_diversity, path:[{ hop, type, proxy_type, ip, port, country, confidential }], privacy_score }

## 4. Error Pattern
Error JSON:
{ error: "error_code", message: "Human readable", timestamp, request_id? }
Common: invalid_request, unauthorized, forbidden, rate_limited, insufficient_balance, invalid_work, proxy_unavailable.
Retry Guidance: Only retry on internal_error or transient network. Respect rate_limited with backoff.

## 5. Rate Limits (App-Safe Defaults)
Mining work: ≥10s spacing per wallet.
Proxy endpoints: ≤10/min.
Wallet ops: ≤60/hour typical.
Cache /stats for 30s, /api/blockchain/network for 15s.

## 6. Security Notes
- Never expose raw primary wallet address; use provided link (receiver) address externally.
- Always sign or auth key-protected endpoints.
- Do not resend identical mining submission after accepted/rejected.
- Treat mnemonic endpoints as NON-PRODUCTION secure (simplified derivation).

## 7. Quick JS Example
```javascript
import fetch from 'node-fetch';
const base = 'https://zerolinkchain.com/api';
const headers = { 'Authorization': 'Bearer '+process.env.ZLC_API_KEY };

async function miningCycle(wallet){
  const work = await (await fetch(`${base}/api/mining/work?wallet=${wallet}`, { headers })).json();
  // ... compute nonce + hash ...
  const submit = await (await fetch(`${base}/api/mining/submit`, { 
    method:'POST', headers:{...headers,'Content-Type':'application/json'},
    body: JSON.stringify({ wallet, work_id: work.work_id, nonce:1234567, hash:'hash_here' })
  })).json();
  return submit;
}
```

## 8. Quick Python Example
```python
import os, requests
BASE = 'https://zerolinkchain.com/api'
HEADERS = { 'Authorization': f"Bearer {os.environ['ZLC_API_KEY']}" }

r = requests.get(f"{BASE}/stats", headers=HEADERS).json()
work = requests.get(f"{BASE}/api/mining/work", params={'wallet':'miner001'}, headers=HEADERS).json()
# submit = requests.post(f"{BASE}/api/mining/submit", json={...}, headers=HEADERS).json()
```

## 9. Typical UX Sequence
1. User creates/imports wallet (mnemonic or priv key).
2. App fetches balance + stats.
3. If mining: start cycle loop.
4. If using VPN: discover → route plan → connect.
5. Show realtime events via WebSocket.

## 10. Fast Checklist (Before Production)
[ ] Handle 401/403 gracefully.
[ ] Throttle mining work requests.
[ ] Cache global stats.
[ ] Backoff on 429.
[ ] Hide private keys & mnemonics.
[ ] Validate transfer amount > 0 & ≤ balance.

---
Short guide complete.
