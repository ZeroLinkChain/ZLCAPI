# ZeroLinkChain API – Operational Instructions for AI Agents
## Version: 1.0.0  
Last Sync With API Docs: 2025-09-01

---
## 1. Purpose
This document converts the public API reference into *actionable operational rules* for an AI agent that must: 
- Select correct endpoints
- Sequence calls into coherent workflows
- Respect authentication & rate limits
- Handle errors, retries, and backoff
- Produce safe, deterministic, idempotent interactions
- Optimize latency & reduce redundant traffic

Use this as the single source of truth for automated reasoning & execution.

---
## 2. Environments & Base URLs
| Environment | Base URL | Notes |
|-------------|----------|-------|
| Production  | https://zerolinkchain.com/api/ | Primary target (default) |
| Development | https://dev-http.zerolinkchain.com/api/ | Use only if explicitly requested |
| Local       | http://localhost:8001/ | For local testing / sandbox |
| Legacy Proxy Wrapper | https://zerolinkchain.com/api.php?e= | Avoid unless backward compatibility required |

Selection Rule: Default to Production unless user explicitly specifies dev/local.

---
## 3. Authentication Modes
1. API Key (preferred for scripted ops):  
   Header: `Authorization: Bearer <API_KEY>`
2. Wallet Signature (when keyless or user-specified):  
   Headers:  
   - `X-Wallet-Address: <address>`  
   - `X-Wallet-Signature: <request_signature>`

Decision Logic:
- If API key provided in context → use Bearer.
- If only wallet & signing capability provided → use wallet headers.
- Never mix unless explicitly required.

Do NOT log secrets. Mask keys after first validation.

---
## 4. Core Functional Domains
| Domain | Purpose | Primary Endpoints |
|--------|---------|-------------------|
| Health & Meta | Service readiness | `/health`, `/stats` |
| Mining Pool | Work acquisition & submission | `/api/mining/work`, `/api/mining/submit`, `/api/mining/stats` |
| Proxy / VPN | Discovery, routing, lifecycle | `/api/proxy/discover`, `/api/proxy/route`, `/api/proxy/register`, `/api/proxy/heartbeat`, `/api/proxy/hop`, `/api/proxy/scan-subnet` |
| Wallet | Balance & transfers | `/api/wallet/balance`, `/api/wallet/transfer`, `/api/wallet/history` |
| Wallet Key Access | Deterministic key derivation & import | `/api/v1/wallet/mnemonic/create`, `/api/v1/wallet/mnemonic/import`, `/api/v1/wallet/privkey/import` |
| Blockchain | Chain state | `/api/blockchain/block/{height}`, `/api/blockchain/network` |
| Statistics | Aggregated proxy stats | `/proxy/stats` |
| Realtime | Event streaming | WebSocket `wss://zerolinkchain.com/ws` |

---
## 5. Rate Limiting & Backoff Strategy
| Category | Limit (Approx) | Default Backoff Strategy |
|----------|----------------|---------------------------|
| Mining Work | 1 request / 10s / wallet | If `rate_limited`: wait `retry_after` or min(10s, header reset) |
| Proxy API | 10 / minute | Exponential: 6s, 12s, 24s (cap 60s) |
| Wallet API | 60 / hour | Linear: wait until reset header |
| Stats API | 100 / hour | Cache aggressively (TTL 30–60s) |
| Blockchain API | 1000 / hour | Cache per block height (immutable) |

Headers to watch: `X-RateLimit-Remaining`, `X-RateLimit-Reset`. On 429 or `rate_limited`, apply strategy; never hammer.

---
## 6. Error Handling Framework
Standard Error JSON:
```json
{
  "error": "error_code",
  "message": "Human readable error message",
  "timestamp": 0,
  "request_id": "req_..."
}
```

| Code | Class | Agent Action |
|------|-------|--------------|
| invalid_request | Client | Validate inputs; do not retry unchanged |
| unauthorized | Auth | Acquire / refresh creds; retry once |
| forbidden | AuthZ | Abort; escalate to user |
| not_found | Data | Verify parameters; if block height > current network height → wait & retry later |
| rate_limited | Throttle | Apply backoff (see §5) |
| internal_error | Server | Retry with jitter (max 3 attempts) |
| wallet_not_found | Domain | Prompt for wallet creation / selection |
| insufficient_balance | Domain | Abort transfer; report required funds |
| invalid_work | Mining | Fetch new work before re-submission |
| proxy_unavailable | Network | Re-discover proxies or relax constraints |

Retry Envelope:
```
max_attempts: 3
base_delay: 2s
jitter: random(0–400ms)
```
Never retry non-idempotent transfer after ambiguous success without verifying history.

---
## 7. Data Field Normalization
| Field | Type | Notes |
|-------|------|-------|
| timestamp | int (epoch seconds) | Convert to ISO8601 only for presentation |
| difficulty | int | Mining target complexity |
| hash_rate | string | Preformatted (e.g., "1.25 MH/s") – keep original & parse if needed |
| balance / rewards / fees | float | Maintain precision; avoid binary rounding in recalculation |
| route.path | array | Ordered hops; maintain order |

Validation Rule: Reject floats with >12 decimal digits when constructing new requests.

---
## 8. Caching Guidelines
| Resource | Cache Key | TTL | Invalidation |
|----------|-----------|-----|--------------|
| `/stats` | stats_global | 30s | Manual refresh if user explicitly requests latest |
| `/api/blockchain/block/{h}` | block_{h} | Infinite (immutable) | N/A |
| `/api/blockchain/network` | network_meta | 15s | Height increase event |
| Proxy discovery results | proxies_{limit}_{filters} | 15s | On route planning requiring stricter constraints |
| Wallet balance | wallet_bal_{addr} | 10s | On transfer affecting that wallet |
| Wallet history | wallet_hist_{addr}_{limit} | 30s | On new tx observed (websocket) |

Cache Insertion Only After 2xx Success.

---
## 9. Workflow Playbooks
### 9.1 Mining Work Cycle
1. Ensure last work request ≥10s ago.
2. GET `/api/mining/work?wallet=...`.
3. Compute PoW (external).
4. POST `/api/mining/submit` with nonce/hash.
5. If `accepted` → update wallet stats & invalidate balance cache.
6. If `invalid_proof_of_work` → fetch fresh work (no immediate retry of same payload).

### 9.2 Wallet Transfer
1. Fetch balances for `from` wallet.
2. Validate `amount <= balance - fee_estimate` (fee nominal 0.001; confirm after response).
3. POST transfer.
4. If success → invalidate both wallets' balance & histories.
5. If uncertain (network error after send) → query history for `transaction_id` pattern (if known); DO NOT blindly retry.

### 9.3 Proxy Route Planning

### 9.4 Wallet Key / Mnemonic Lifecycle
1. Create new mnemonic wallet: POST `/api/v1/wallet/mnemonic/create` → receives mnemonic + privateKey + address (simplified derivation).
2. Import mnemonic: POST `/api/v1/wallet/mnemonic/import` with `{ mnemonic }` → returns deterministic address & balance.
3. Import private key: POST `/api/v1/wallet/privkey/import` with `{ privateKey }` → derives address & returns balance.
4. Security: Mark simplified mnemonic as NON-PRODUCTION if user intends high-value storage; recommend hardened derivation upgrade.

1. Optionally discover proxies (if cache stale or constraints changed).
2. GET `/api/proxy/route?target_country=...&min_bandwidth=...&hops=...`.
3. Validate returned `hops == requested` (unless not specified).
4. If `privacy_score < threshold (e.g., 80)` → attempt route with different parameters (increase hops ≤5) once.

### 9.4 Proxy Node Lifecycle (Registration Actor)
1. POST `/api/proxy/register` (one-time).
2. Schedule heartbeat loop: POST `/api/proxy/heartbeat` before `next_heartbeat`.
3. For each observed user hop: POST `/api/proxy/hop` capturing billing.

### 9.5 Real-Time Event Integration
1. Open WebSocket.
2. Subscribe to required events.
3. On `new_block` → pull `/api/blockchain/block/{height}`; update network cache.
4. On `wallet_transaction` → refresh balance + append to cached history.
5. On `proxy_discovered` → optionally merge into discovery cache.

---
## 10. Input Construction Rules
- Sanitize numeric inputs (positive integers for heights, hops 2–5).
- Enforce `limit` bounds: 1 ≤ limit ≤ 100.
- Reject negative or zero transfer amounts.
- Wallet strings: lowercase alphanumeric + underscore; flag others for confirmation.

---
## 11. Safety & Security Constraints
| Concern | Mitigation |
|---------|-----------|
| Credential leakage | Never echo full API key; mask after first 4 chars |
| Replay risk (transfers) | Perform existence check in history before retry |
| Over-polling | Respect TTL & rate headers |
| Data tampering | Do not trust derived client-side balances—always refetch canonical on sensitive ops |
| Precision loss | Avoid summing floating rewards repeatedly; rely on server totals |

---
## 12. Response Classification
| Status | Action |
|--------|--------|
| 2xx | Parse, normalize, cache (if eligible) |
| 4xx | Diagnose; correct inputs or escalate |
| 5xx | Retry envelope (see §6) |
| Non-JSON | Treat as transient server error (unless documented) |

---
## 13. Retry Algorithm (Pseudo)
```python
def retry_request(op, classify, max_attempts=3, base_delay=2.0):
    attempt = 1
    while attempt <= max_attempts:
        resp = op()
        action = classify(resp)
        if action == 'return':
            return resp
        if action == 'no_retry':
            raise resp.error
        if attempt == max_attempts:
            raise TimeoutError('exhausted attempts')
        sleep(base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.4))
        attempt += 1
```

---
## 14. Idempotency Guidelines
| Operation | Idempotent? | Strategy |
|-----------|-------------|----------|
| GET endpoints | Yes | Cache & reuse |
| Work retrieval | Yes (time-gated) | Single active work per wallet per cycle |
| Mining submit | No (result depends on nonce) | Do not resend identical payload unless server error without response body |
| Wallet transfer | No | Require post-check before retry |
| Proxy register | Conditionally (unique ip:port) | If duplicate, treat as success |
| Heartbeat | Yes | Safe to retry after network fail |
| Hop record | No (billing) | Confirm absence before replay (if server provides id) |

---
## 15. Performance Heuristics
- Prefer aggregated `/stats` over multiple granular calls when user asks for “overall state”.
- Use WebSocket events to trigger selective refresh instead of periodic polling loops.
- Coalesce simultaneous wallet balance refresh requests per address (promise batching pattern).

---
## 16. Data Modeling (Suggested Internal Types)
```typescript
interface MiningWork { work_id: string; wallet: string; target: string; difficulty: number; timestamp: number; algorithm: string; }
interface MiningSubmitResult { work_id: string; wallet: string; status: 'accepted'|'rejected'; reward?: number; reason?: string; proof?: string; }
interface WalletBalance { wallet: string; balance: number; mining_rewards: number; proxy_fees: number; service_fees: number; blocks_mined: number; proxy_hops: number; active: boolean; created: number; }
interface ProxyNode { id: string; ip: string; port: number; type: string; country: string; bandwidth_mbps: number; latency_ms: number; reliability: number; last_seen: number; active: boolean; }
interface RouteHop { hop: number; type: 'entry'|'middle'|'exit'; proxy_type: string; ip: string; port: number; country: string; confidential: boolean; }
```

---
## 17. Sequencing Examples
### A. “Show me current network + last block”
1. GET `/api/blockchain/network` (cache 15s)
2. Extract `height` → GET `/api/blockchain/block/{height}` (cache forever)

### B. “Transfer 50 units from A to B”
1. GET balance (A) → ensure balance ≥ 50 + fee
2. POST transfer
3. Refresh balances (A & B)
4. Append transaction to history caches

### C. “Find a high privacy route (≥90 score)”
1. GET `/api/proxy/route?hops=5`
2. If `privacy_score < 90` → adjust `min_bandwidth` downward or increase ASN diversity attempt (re-run once)

---
## 18. WebSocket Event Handling Table
| Event | Triggered Action |
|-------|------------------|
| new_block | Fetch block; update network height; invalidate network cache |
| mining_work | (If wallet subscribed) request new work if not holding active task |
| proxy_discovered | Merge proxy node into discovery cache |
| wallet_transaction | Refresh that wallet's balance & history |

Connection Resilience:
- Heartbeat ping every 25s.
- Reconnect with backoff (2s, 5s, 10s, cap 30s).

---
## 19. Logging Template (Internal Agent)
| Level | Example |
|-------|---------|
| INFO | mining.submit accepted work_id=ZLC_xxx reward=0.156789 |
| WARN | rate_limited endpoint=/api/mining/work retry_in=7s |
| ERROR | transfer failed insufficient_balance requested=100 available=50 |
| DEBUG | cache.miss key=wallet_bal_user123 |

Exclude sensitive headers from logs.

---
## 20. Validation Checklist per Request
| Check | Apply To |
|-------|----------|
| Wallet format | All wallet-based endpoints |
| Numeric bounds | limits, hops, amount |
| Rate window respected | mining, proxy heavy endpoints |
| Cache freshness | prefer cached if TTL valid |
| Idempotency guard | transfers, mining submit |

---
## 21. Security Red Flags (Abort If)
- Response includes unexpected executable content.
- Timestamp skew > 5 minutes (possible clock/issues) – warn user.
- Repeated inconsistent balances (3 consecutive mismatches) – stop financial operations.

---
## 22. Extensibility Hooks
Prepare to accept future endpoints by implementing a generic GET/POST wrapper:
```python
def api_call(method, path, params=None, body=None, auth=None):
    # Build URL from base + path
    # Inject headers per auth mode
    # Serialize JSON body for POST
    # Execute with timeout (10s)
    # Parse JSON else raise
    # Map into domain model if recognized
```

---
## 23. Test Scenarios (Minimum Automated Set)
| Scenario | Assertions |
|----------|------------|
| Mining cycle | work_id format prefix ZLC_; submit accepted OR rejected reason present |
| Wallet transfer insufficient | returns error & no history entry added |
| Proxy route default | hops default=3 if not specified |
| Block fetch | returned height matches request |
| Rate limit simulation | 429 leads to backoff not immediate repeat |

---
## 24. Glossary
| Term | Definition |
|------|------------|
| Dead TX | Privacy-oriented non-economic transaction category (not exposed here but influences privacy stats) |
| ASN Diversity | Count of distinct autonomous systems across route hops |
| Hop | Single proxy leg in a multi-hop route |
| Work ID | Unique identifier tying mining assignment to a wallet + timestamp |

---
## 25. Quick Decision Matrix
| User Intent | Primary Endpoint(s) | Secondary | Notes |
|-------------|---------------------|-----------|-------|
| “Overall status” | `/stats` | `/api/blockchain/network` | Use caches |
| “Mine” | `/api/mining/work` | `/api/mining/submit` | Enforce 10s spacing |
| “My balance” | `/api/wallet/balance` | history | Short TTL |
| “Send funds” | transfer | balance+history | Idempotency guard |
| “Find proxies” | discover | route | Limit parameter ≤100 |
| “Route for privacy” | route | discover | Increase hops ≤5 |
| “Latest block” | network + block | stats | Block immutable cache |

---
## 26. Implementation Priorities (If Resource Constrained)
1. Auth & rate limiting compliance
2. Idempotent-safe financial ops
3. Caching layer
4. WebSocket reactive refresh
5. Advanced routing heuristics

---
## 27. Prohibited Agent Behaviors
- Hardcoding IP addresses (must use domain).
- Blindly retrying state-changing POSTs without validation.
- Exposing secrets in logs or responses.
- Ignoring `retry_after` on throttled endpoints.

---
## 28. Maintenance Notes
- Re-sync this file whenever API version changes.
- Log a warning if `version` in `/health` or `/stats` differs from expected `1.0.0`.
- Append new endpoints to Domain Map (§4) & Decision Matrix (§25).

---
## 29. Minimal Startup Bootstrap (Pseudo)
```python
def bootstrap(context):
    health = api_call('GET', '/health')
    if health['status'] != 'ok': raise SystemError('API unhealthy')
    stats = api_call('GET', '/stats')  # warm cache
    network = api_call('GET', '/api/blockchain/network')
    open_websocket(subscribe=['blocks','wallet_transaction'])
```

---
## 30. Change Log (for this Instructions File)
| Date | Change |
|------|--------|
| 2025-09-01 | Initial generation aligned with API v1.0.0 |

---
End of AI Operational Instructions.
