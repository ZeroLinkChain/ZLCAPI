# ZeroLinkChain API Quick Reference
## Developer Cheat Sheet

### Base URLs
```
Production:  https://zerolinkchain.com/api/
Legacy:      https://zerolinkchain.com/api.php?e=
Local:       http://localhost:8001/
```

### Authentication
```http
Authorization: Bearer YOUR_API_KEY
X-Wallet-Address: your_wallet_address
```

---

## Core Endpoints

### System Status
```bash
# Get system statistics
curl "https://zerolinkchain.com/api.php?e=stats"

# Health check
curl "http://localhost:8001/health"
```

### Mining Pool

```bash
# Get mining work
curl "http://localhost:8001/api/mining/work?wallet=miner001"

# Submit work
curl -X POST -H "Content-Type: application/json" \
  -d '{"wallet":"miner001","work_id":"ZLC_123","nonce":1234567,"hash":"000000abc..."}' \
  "http://localhost:8001/api/mining/submit"

# Get mining stats
curl "http://localhost:8001/api/mining/stats?wallet=miner001"
```

### Proxy Network

```bash
# Discover proxies
curl "https://zerolinkchain.com/api.php?e=hosts"
curl "http://localhost:8001/api/proxy/discover?limit=10"

# Register proxy node
curl -X POST -H "Content-Type: application/json" \
  -d '{"wallet":"proxy001","ip":"203.0.113.15","port":8080}' \
  "http://localhost:8001/api/proxy/register"

# Send heartbeat
curl -X POST -H "Content-Type: application/json" \
  -d '{"wallet":"proxy001"}' \
  "http://localhost:8001/api/proxy/heartbeat"

# Record hop
curl -X POST -H "Content-Type: application/json" \
  -d '{"provider_wallet":"proxy001","user_wallet":"user123"}' \
  "http://localhost:8001/api/proxy/hop"
```

## Wallet Operations

```bash
# Get balance
curl "http://localhost:8001/api/wallet/balance?wallet=user123"

# Transfer funds
curl -X POST -H "Content-Type: application/json" \
  -d '{"from":"sender123","to":"receiver456","amount":100.0}' \
  "http://localhost:8001/api/wallet/transfer"

# Get transaction history
curl "http://localhost:8001/api/wallet/history?wallet=user123&limit=10"
```

### New (Mnemonic / Private Key - Dev Only)
```
POST /v1/wallet/mnemonic/create -> { mnemonic, privateKey, address }
POST /v1/wallet/mnemonic/import { mnemonic }
POST /v1/wallet/privkey/import { privateKey }
```
NOTE: Non-production derivation; do not use real seeds.

See `API_DOCUMENTATION.md` for extended security notes.

---

## Response Formats

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "timestamp": 1756769132
}
```

### Error Response
```json
{
  "error": "error_code",
  "message": "Human readable message",
  "timestamp": 1756769132
}
```

### Mining Work Response
```json
{
  "work_id": "ZLC_miner001_1756769132_23c6",
  "wallet": "miner001",
  "target": "00000000697351ff4aec29cdbaabf2fbe3467cc254f81be8e78d765a2e63339f",
  "difficulty": 1089380,
  "timestamp": 1756769132,
  "status": "new_work",
  "algorithm": "sha256_pow"
}
```

### System Stats Response
```json
{
  "status": "production",
  "version": "1.0.0",
  "deployment_status": "live",
  "blockchain": {
    "height": 2047,
    "hash_rate": 1250000.5,
    "type": "mainnet"
  },
  "mining": {
    "active_miners": 156,
    "total_hash_rate": "1.25 MH/s",
    "status": "pool_active",
    "pool_fee": 1.0
  },
  "vpn": {
    "connected_hosts": 23,
    "total_bandwidth": 15000,
    "status": "infrastructure_active"
  }
}
```

### Proxy Discovery Response
```json
{
  "status": "ok",
  "count": 5,
  "nodes": [
    {
      "id": "http_proxy_185.199.228.15_8080",
      "ip": "185.199.228.15",
      "port": 8080,
      "type": "HTTP",
      "country": "US",
      "bandwidth_mbps": 15,
      "latency_ms": 85,
      "reliability": 0.94,
      "active": true
    }
  ]
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| `invalid_request` | Malformed request |
| `unauthorized` | Authentication required |
| `forbidden` | Access denied |
| `not_found` | Resource not found |
| `rate_limited` | Too many requests |
| `wallet_not_found` | Wallet doesn't exist |
| `insufficient_balance` | Not enough funds |
| `invalid_work` | Mining work invalid |
| `proxy_unavailable` | No proxies available |

---

## Rate Limits

| Endpoint Type | Limit |
|---------------|-------|
| Mining API | 1 req/10s per wallet |
| Proxy API | 10 req/min |
| Wallet API | 60 req/hour |
| Stats API | 100 req/hour |

---

## SDK Examples

### JavaScript
```javascript
const ZLC = require('zerolinkchain-sdk');
const client = new ZLC({ apiKey: 'your_key' });

// Get mining work
const work = await client.mining.getWork('miner001');

// Submit work
const result = await client.mining.submit({
  wallet: 'miner001',
  work_id: work.work_id,
  nonce: 1234567,
  hash: 'calculated_hash'
});

// Discover proxies
const proxies = await client.proxy.discover({ limit: 10 });
```

### Python
```python
from zerolinkchain import ZeroLinkChainAPI

client = ZeroLinkChainAPI(api_key='your_key')

# Get wallet balance
balance = client.wallet.get_balance('user123')

# Transfer funds
result = client.wallet.transfer(
    from_wallet='sender',
    to_wallet='receiver',
    amount=100.0
)
```

### cURL Scripts
```bash
#!/bin/bash
API_BASE="http://localhost:8001"
WALLET="miner001"

# Get work and mine
WORK=$(curl -s "$API_BASE/api/mining/work?wallet=$WALLET")
WORK_ID=$(echo $WORK | jq -r '.work_id')
TARGET=$(echo $WORK | jq -r '.target')

# Calculate nonce (simplified)
NONCE=1234567
HASH="000000abc123def456..."

# Submit work
curl -X POST -H "Content-Type: application/json" \
  -d "{\"wallet\":\"$WALLET\",\"work_id\":\"$WORK_ID\",\"nonce\":$NONCE,\"hash\":\"$HASH\"}" \
  "$API_BASE/api/mining/submit"
```

---

## WebSocket API

### Connection
```javascript
const ws = new WebSocket('wss://zerolinkchain.com/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    action: 'subscribe',
    events: ['blocks', 'mining', 'proxy_updates']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data.event, data.data);
};
```

### Event Types
- `new_block`: New block mined
- `mining_work`: New work available
- `proxy_discovered`: New proxy found
- `wallet_transaction`: Transaction occurred

---

## Testing

### Test Mining Pool
```bash
# Test complete mining flow
./test_mining.sh miner001

# Test proxy discovery
curl "http://localhost:8001/api/proxy/discover?limit=5"

# Test wallet operations
./test_wallet.sh user123 100.0
```

### Load Testing
```bash
# Apache Bench
ab -n 1000 -c 10 "http://localhost:8001/health"

# Mining work requests
ab -n 100 -c 5 "http://localhost:8001/api/mining/work?wallet=test"
```

---

## Deployment

### Docker
```dockerfile
FROM ubuntu:20.04
RUN apt-get update && apt-get install -y \
    libssl-dev libsqlite3-dev libcurl4-openssl-dev libjson-c-dev
COPY c_api_server/zl_api_server /usr/local/bin/
EXPOSE 8001
CMD ["zl_api_server", "--port", "8001"]
```

### SystemD Service
```ini
[Unit]
Description=ZeroLinkChain API Server
After=network.target

[Service]
Type=simple
User=zerolinkchain
ExecStart=/opt/zerolinkchain/c_api_server/zl_api_server --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Monitoring

### Health Checks
```bash
# API health
curl "http://localhost:8001/health"

# Database health
sqlite3 blockchain.db "SELECT COUNT(*) FROM wallets;"

# System stats
curl "https://zerolinkchain.com/api.php?e=stats" | jq '.mining.active_miners'
```

### Metrics
- Active miners count
- Proxy nodes available
- API response times
- Error rates
- Transaction volume

---

*Quick Reference v1.0.0*  
*Last Updated: 2025-09-01*
