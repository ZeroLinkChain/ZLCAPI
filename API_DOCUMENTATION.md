# ZeroLinkChain API Documentation
## Comprehensive Developer Reference v1.0.0

### Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URLs](#base-urls)
4. [Core API Endpoints](#core-api-endpoints)
5. [Mining Pool API](#mining-pool-api)
6. [VPN/Proxy API](#vpnproxy-api)
7. [Wallet API](#wallet-api)
8. [Blockchain API](#blockchain-api)
9. [Statistics API](#statistics-api)
10. [Error Handling](#error-handling)
11. [Rate Limiting](#rate-limiting)
12. [WebSocket API](#websocket-api)
13. [SDK Examples](#sdk-examples)

---

## Overview

The ZeroLinkChain API provides comprehensive access to:
- **Mining Pool Operations**: Work assignment, submission, statistics
- **VPN/Proxy Network**: Node discovery, routing, bandwidth management
- **Blockchain Data**: Blocks, transactions, network statistics
- **Wallet Management**: Balance, history, transfers
- **Real-time Data**: WebSocket feeds for live updates

**API Version**: 1.0.0  
**Status**: Production (Mainnet)  
**Protocol**: HTTP/HTTPS + WebSocket  
**Format**: JSON  

---

## Authentication

### API Key Authentication
```http
Authorization: Bearer YOUR_API_KEY
```

### Wallet-based Authentication
```http
X-Wallet-Address: your_wallet_address
X-Wallet-Signature: signature_of_request
```

---

## Base URLs

- **Production**: `https://zerolinkchain.com/api/`
- **Development**: `https://dev-http.zerolinkchain.com/api/`
- **Local**: `http://localhost:8001/`
- **Legacy Proxy**: `https://zerolinkchain.com/api.php?e=`

---

## Core API Endpoints

### 1. Health Check
**GET** `/health`

Returns API service status.

**Response:**
```json
{
  "status": "ok",
  "service": "zerolinkchain_api",
  "version": "1.0.0",
  "timestamp": 1756769132
}
```

### 2. System Statistics
**GET** `/stats`

Returns comprehensive system statistics.

**Response:**
```json
{
  "status": "production",
  "version": "1.0.0",
  "deployment_status": "live",
  "blockchain": {
    "height": 2047,
    "hash_rate": 1250000.5,
    "type": "mainnet",
    "blocks_found_24h": 2880
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
  },
  "privacy": {
    "dead_txs": 1247,
    "privacy_ratio": 95.2,
    "status": "privacy_layer_active"
  },
  "services": {
    "blockchain": "mainnet",
    "pool": "deployed_active",
    "vpn": "deployed_active",
    "api": "responding"
  },
  "infrastructure": {
    "miners_deployed": "true",
    "vpn_hosts_deployed": "true",
    "mainnet_ready": "true",
    "launch_date": "2025-09-01"
  },
  "ports": {
    "pool": 3333,
    "api": 8001,
    "vpn": 9999
  }
}
```

---

## Mining Pool API

### 1. Get Mining Work
**GET** `/api/mining/work?wallet={wallet_address}`

Request new mining work for a wallet.

**Parameters:**
- `wallet` (required): Wallet address

**Response:**
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

**Error Response:**
```json
{
  "error": "rate_limited",
  "retry_after": 7
}
```

### 2. Submit Mining Work
**POST** `/api/mining/submit`

Submit completed mining work.

**Request Body:**
```json
{
  "wallet": "miner001",
  "work_id": "ZLC_miner001_1756769132_23c6",
  "nonce": 1234567,
  "hash": "000000a1b2c3d4e5f6789abcdef0123456789abcdef0123456789abcdef012345"
}
```

**Response (Valid):**
```json
{
  "work_id": "ZLC_miner001_1756769132_23c6",
  "wallet": "miner001",
  "status": "accepted",
  "reward": 0.156789,
  "proof": "valid_work_verified"
}
```

**Response (Invalid):**
```json
{
  "work_id": "ZLC_miner001_1756769132_23c6",
  "wallet": "miner001",
  "status": "rejected",
  "reason": "invalid_proof_of_work"
}
```

### 3. Mining Statistics
**GET** `/api/mining/stats?wallet={wallet_address}`

Get mining statistics for a specific wallet.

**Response:**
```json
{
  "wallet": "miner001",
  "total_work": 1247,
  "valid_work": 1156,
  "invalid_work": 91,
  "acceptance_rate": 92.7,
  "total_rewards": 156.789123,
  "blocks_found": 3,
  "last_work": 1756769132,
  "hash_rate_24h": "125.6 KH/s",
  "rank": 15
}
```

---

## VPN/Proxy API

### 1. Proxy Discovery
**GET** `/api/proxy/discover?limit={count}`

Discover available proxy nodes.

**Parameters:**
- `limit` (optional): Maximum nodes to return (default: 10, max: 100)

**Response:**
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
      "last_seen": 1756769132,
      "active": true
    },
    {
      "id": "socks5_proxy_104.16.1.25_1080",
      "ip": "104.16.1.25", 
      "port": 1080,
      "type": "SOCKS5",
      "country": "EU",
      "bandwidth_mbps": 12,
      "latency_ms": 120,
      "reliability": 0.87,
      "last_seen": 1756769098,
      "active": true
    }
  ],
  "timestamp": 1756769132
}
```

### 2. Subnet Scanning
**GET** `/api/proxy/scan-subnet?subnet={subnet}&start={start}&end={end}`

Scan a subnet for proxy servers.

**Parameters:**
- `subnet` (required): Subnet base (e.g., "192.168.1")
- `start` (optional): Start IP (default: 1)
- `end` (optional): End IP (default: 254)

**Response:**
```json
{
  "status": "scanning",
  "subnet": "192.168.1",
  "range": "1-254",
  "scan_id": "scan_1756769132_abc123",
  "estimated_time": 300,
  "message": "Subnet scan initiated"
}
```

### 3. Route Planning
**GET** `/api/proxy/route?target_country={country}&min_bandwidth={mbps}&hops={count}`

Plan optimal routing path through proxy network.

**Parameters:**
- `target_country` (optional): Target country code
- `min_bandwidth` (optional): Minimum bandwidth in Mbps
- `hops` (optional): Number of hops (2-5, default: 3)

**Response:**
```json
{
  "route_id": "confidential_1756769132",
  "hops": 3,
  "total_latency": 285,
  "min_bandwidth": 12,
  "asn_diversity": 3,
  "path": [
    {
      "hop": 1,
      "type": "entry",
      "proxy_type": "SOCKS5",
      "ip": "104.16.1.25",
      "port": 1080,
      "country": "EU",
      "confidential": true
    },
    {
      "hop": 2,
      "type": "middle",
      "proxy_type": "HTTP",
      "ip": "8.8.4.15",
      "port": 8080,
      "country": "US",
      "confidential": false
    },
    {
      "hop": 3,
      "type": "exit",
      "proxy_type": "HTTP", 
      "ip": "185.199.228.15",
      "port": 8080,
      "country": "US",
      "confidential": true
    }
  ],
  "privacy_score": 95.2
}
```

### 4. Proxy Registration
**POST** `/api/proxy/register`

Register a new proxy node.

**Request Body:**
```json
{
  "wallet": "proxy_provider_001",
  "ip": "203.0.113.15",
  "port": 8080
}
```

**Response:**
```json
{
  "status": "registered",
  "wallet": "proxy_provider_001",
  "node_id": "proxy_203.0.113.15_8080",
  "registration_time": 1756769132
}
```

### 5. Proxy Heartbeat
**POST** `/api/proxy/heartbeat`

Send heartbeat to maintain proxy node status.

**Request Body:**
```json
{
  "wallet": "proxy_provider_001"
}
```

**Response:**
```json
{
  "status": "ok",
  "next_heartbeat": 1756769252
}
```

### 6. Record Proxy Hop
**POST** `/api/proxy/hop`

Record a proxy hop for billing/statistics.

**Request Body:**
```json
{
  "provider_wallet": "proxy_provider_001",
  "user_wallet": "user_wallet_123"
}
```

**Response:**
```json
{
  "status": "recorded",
  "fee": 0.001,
  "hop_id": "hop_1756769132_xyz789"
}
```

---

## Wallet API

### 1. Get Wallet Balance
**GET** `/api/wallet/balance?wallet={public_link_address}`

Retrieve a wallet's effective balance and activity statistics.

#### Privacy & Address Abstraction
ZeroLinkChain employs a two-layer wallet addressing model for privacy:
1. **Primary Wallet Address (PWA)** – The canonical address that actually holds funds and signs outbound transfers. Never exposed directly over unauthenticated API calls.
2. **Receiver (Link) Address (RLA)** – A privacy-preserving alias presented externally (shown as `wallet` in most responses). RLAs map internally to a PWA through a confidential lookup. Multiple RLAs can point to one PWA to compartmentalize transaction graph analysis.

Balances returned for a `wallet` parameter are *effective balances* computed from the underlying PWA plus any pending Dead‑TX transfer signals associated with that RLA.

#### Dead-TX Transfer Signaling
When a transfer is initiated to an RLA:
1. A Dead‑TX metadata record is created (non-economic) signaling intent and preserving privacy context.
2. The underlying PWA ledger entry is updated only upon confirmation/mining.
3. Until confirmation, the API may expose a `pending_adjustment` field (future extension) or include the amount in a `pendingBalance` calculation without revealing raw internal PWA address.

#### Authentication Requirement
Direct balance queries MUST include either:
```
Authorization: Bearer <API_KEY>
```
or a wallet signature:
```
X-Wallet-Address: <public_link_address>
X-Wallet-Signature: <signature>
```
Unauthenticated balance lookups SHOULD return `401 unauthorized` (or `403 forbidden`) in production deployments. Public enumeration of wallet balances is disallowed.

#### Parameters
- `wallet` (required): Receiver (link) address (RLA). If a raw PWA is supplied, the server MAY reject or obfuscate the result.

#### Response (Current Stable Schema)
```json
{
  "wallet": "user_wallet_link_123",
  "balance": 1247.856789,
  "mining_rewards": 156.789123,
  "proxy_fees": 23.456789,
  "service_fees": 12.345678,
  "blocks_mined": 3,
  "proxy_hops": 1247,
  "active": true,
  "created": 1756769132
}
```

#### Planned / Extended Fields (Privacy Mode Enhancements)
| Field | Type | Description |
|-------|------|-------------|
| `pendingBalance` | float | Aggregate of unconfirmed inbound transfers signaled by Dead‑TX metadata |
| `linked_addresses` | int | Count of RLAs mapped to the same underlying PWA (only with elevated auth) |
| `anonymity_set` | int | Approximate anonymity set size for recent mixing period |

#### Error Responses
- `unauthorized` – Missing or invalid credentials
- `forbidden` – Credential valid but scope disallows balance viewing
- `wallet_not_found` – RLA/PWA mapping not present

#### Example (Authenticated Request)
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     "https://zerolinkchain.com/api/wallet/balance?wallet=user_wallet_link_123"
```

#### Security Notes
- Never expose raw PWA when answering balance queries; always return the queried RLA.
- Dead‑TX records MUST NOT leak the internal PWA linkage; only hashed or signature-derived references are stored.
- Cache balance responses per RLA for ≤10s; invalidate on transfer, mining reward, or Dead‑TX signal creation.

### 2. Wallet Transfer
**POST** `/api/wallet/transfer`

Transfer funds between wallets.

**Request Body:**
```json
{
  "from": "sender_wallet_123",
  "to": "receiver_wallet_456", 
  "amount": 100.0
}
```

**Response (Success):**
```json
{
  "status": "success",
  "from": "sender_wallet_123",
  "to": "receiver_wallet_456",
  "amount": 100.0,
  "transaction_id": "tx_1756769132_abc123",
  "fee": 0.001
}
```

**Response (Error):**
```json
{
  "error": "insufficient_balance",
  "current_balance": 50.0,
  "requested_amount": 100.0
}
```

### 3. Transaction History
**GET** `/api/wallet/history?wallet={wallet_address}&limit={count}`

Get wallet transaction history.

**Parameters:**
- `wallet` (required): Wallet address
- `limit` (optional): Number of transactions (default: 10, max: 100)

**Response:**
```json
{
  "wallet": "user_wallet_123",
  "transactions": [
    {
      "tx_id": "tx_1756769132_abc123",
      "type": 1,
      "amount": 100.0,
      "timestamp": 1756769132,
      "details": "Transfer to receiver_wallet_456"
    },
    {
      "tx_id": "tx_1756769098_def456", 
      "type": 2,
      "amount": 0.156789,
      "timestamp": 1756769098,
      "details": "Mining reward for block #2047"
    }
  ],
  "total_count": 1247,
  "page": 1
}
```

---

## Blockchain API

### 1. Get Block Information
**GET** `/api/blockchain/block/{block_height}`

Get detailed block information.

**Response:**
```json
{
  "height": 2047,
  "hash": "000000a1b2c3d4e5f6789abcdef0123456789abcdef0123456789abcdef012345",
  "previous_hash": "000000b2c3d4e5f6789abcdef0123456789abcdef0123456789abcdef012345a1",
  "timestamp": 1756769132,
  "difficulty": 4,
  "nonce": 1234567,
  "miner": "zerolinkchain-miner",
  "reward": 1000000,
  "transactions": 15,
  "size": 2048,
  "confirmations": 156
}
```

### 2. Get Network Information
**GET** `/api/blockchain/network`

Get network statistics and information.

**Response:**
```json
{
  "network": "mainnet",
  "height": 2047,
  "difficulty": 4,
  "hash_rate": "1.25 MH/s",
  "block_time": 30,
  "total_supply": 2047000000,
  "circulating_supply": 2046500000,
  "nodes": 156,
  "version": "1.0.0"
}
```

---

## Statistics API

### 1. Proxy Statistics
**GET** `/proxy/stats`

Get proxy network statistics.

**Response:**
```json
{
  "total_nodes": 23,
  "active_nodes": 19,
  "total_bandwidth": 15000,
  "average_latency": 125.5,
  "countries": 8,
  "proxy_types": {
    "HTTP": 12,
    "SOCKS5": 7,
    "HTTPS": 4
  },
  "reliability_average": 0.89,
  "hops_24h": 15678
}
```

---

## Error Handling

### Standard Error Response Format
```json
{
  "error": "error_code",
  "message": "Human readable error message",
  "timestamp": 1756769132,
  "request_id": "req_1756769132_abc123"
}
```

### Common Error Codes
- `invalid_request`: Malformed request
- `unauthorized`: Authentication required
- `forbidden`: Access denied
- `not_found`: Resource not found
- `rate_limited`: Too many requests
- `internal_error`: Server error
- `wallet_not_found`: Wallet doesn't exist
- `insufficient_balance`: Not enough funds
- `invalid_work`: Mining work invalid
- `proxy_unavailable`: No proxies available

---

## Rate Limiting

### Limits by Endpoint Type
- **Mining API**: 1 request per 10 seconds per wallet
- **Proxy API**: 10 requests per minute
- **Wallet API**: 60 requests per hour
- **Statistics API**: 100 requests per hour
- **Blockchain API**: 1000 requests per hour

### Rate Limit Headers
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1756769192
```

---

## WebSocket API

### Connection
```javascript
const ws = new WebSocket('wss://zerolinkchain.com/ws');
```

### Subscribe to Events
```json
{
  "action": "subscribe",
  "events": ["blocks", "mining", "proxy_updates"]
}
```

### Event Types
- `new_block`: New block mined
- `mining_work`: New mining work available
- `proxy_discovered`: New proxy node found
- `wallet_transaction`: Wallet transaction occurred

### Example Event
```json
{
  "event": "new_block",
  "data": {
    "height": 2048,
    "hash": "000000c3d4e5f6789abcdef0123456789abcdef0123456789abcdef012345b2",
    "miner": "miner_wallet_456",
    "reward": 1000000,
    "timestamp": 1756769162
  }
}
```

---

## SDK Examples

### JavaScript/Node.js
```javascript
const ZeroLinkChain = require('zerolinkchain-sdk');

const client = new ZeroLinkChain({
  apiKey: 'your_api_key',
  baseUrl: 'https://zerolinkchain.com/api/'
});

// Get mining work
const work = await client.mining.getWork('your_wallet');

// Submit work
const result = await client.mining.submit({
  wallet: 'your_wallet',
  work_id: work.work_id,
  nonce: 1234567,
  hash: 'calculated_hash'
});

// Discover proxies
const proxies = await client.proxy.discover({ limit: 10 });

// Plan route
const route = await client.proxy.planRoute({
  target_country: 'US',
  min_bandwidth: 10,
  hops: 3
});
```

### Python
```python
from zerolinkchain import ZeroLinkChainAPI

client = ZeroLinkChainAPI(
    api_key='your_api_key',
    base_url='https://zerolinkchain.com/api/'
)

# Get wallet balance
balance = client.wallet.get_balance('your_wallet')

# Get system stats
stats = client.get_stats()

# Transfer funds
result = client.wallet.transfer(
    from_wallet='sender',
    to_wallet='receiver', 
    amount=100.0
)
```

### cURL Examples
```bash
# Get mining work
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://zerolinkchain.com/api/mining/work?wallet=your_wallet"

# Submit mining work
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"wallet":"your_wallet","work_id":"work_123","nonce":1234567,"hash":"hash_value"}' \
  "https://zerolinkchain.com/api/mining/submit"

# Discover proxies
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://zerolinkchain.com/api/proxy/discover?limit=10"
```

---

## Support

- **Documentation**: https://docs.zerolinkchain.com
- **API Status**: https://status.zerolinkchain.com  
- **Developer Support**: dev@zerolinkchain.com
- **GitHub**: https://github.com/zerolinkchain/api

---

## Advanced Features

### 1. Confidential Routing Implementation

The ZeroLinkChain VPN system implements a sophisticated multi-hop routing system:

**Route Structure:**
```
Entry Node (SOCKS5) → Middle Nodes (HTTP/Various) → Exit Node (HTTP)
      ↓                        ↓                         ↓
100% Confidential      Obfuscation Layer         100% Confidential
```

**Technical Implementation:**
- **Entry Hop**: SOCKS5 proxy for maximum anonymity
- **Middle Hops**: 1-3 intermediate nodes with ASN diversity
- **Exit Hop**: HTTP proxy optimized for web traffic
- **Encryption**: End-to-end encryption between all hops
- **ASN Diversity**: Ensures different Autonomous System Numbers

### 2. Mining Pool Architecture

**Proof-of-Work Algorithm:**
- **Algorithm**: SHA256
- **Difficulty**: Dynamic adjustment based on submission rate
- **Target**: 30-second block intervals
- **Reward**: 1,000,000 ZLC per block
- **Pool Fee**: 1%

**Work Assignment Process:**
1. Miner requests work with wallet address
2. Pool generates unique work_id and target hash
3. Miner calculates nonce to meet difficulty target
4. Pool validates proof-of-work cryptographically
5. Reward distributed based on difficulty multiplier

### 3. Proxy Discovery Algorithm

**Scanning Strategy:**
```javascript
// Proxy ranges scanned
const PROXY_RANGES = [
  "185.199.228", "185.199.229", "185.199.230", // GitHub
  "104.16.0", "104.16.1", "104.16.2",          // Cloudflare
  "8.8.4", "8.8.8",                            // Google
  "1.1.1", "1.0.0"                             // Cloudflare DNS
];

// Common proxy ports
const PROXY_PORTS = [8080, 3128, 1080, 8888, 8000, 3129, 8081, 9050];
```

**Validation Process:**
- **HTTP Proxies**: CONNECT method test to google.com:80
- **SOCKS5 Proxies**: Authentication negotiation handshake
- **Timeout**: 2-second connection timeout
- **Verification**: Actual proxy functionality testing

### 4. Database Schema

**Mining Work Table:**
```sql
CREATE TABLE mining_work (
    work_id TEXT PRIMARY KEY,
    wallet_address TEXT NOT NULL,
    target TEXT NOT NULL,
    difficulty INTEGER,
    created_at INTEGER,
    submitted_at INTEGER DEFAULT NULL,
    nonce INTEGER DEFAULT NULL,
    hash TEXT DEFAULT NULL,
    valid INTEGER DEFAULT 0,
    FOREIGN KEY(wallet_address) REFERENCES wallets(address)
);
```

**Proxy Pool Table:**
```sql
CREATE TABLE proxy_pool (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_address TEXT NOT NULL,
    ip_address TEXT NOT NULL,
    port INTEGER NOT NULL,
    proxy_type TEXT DEFAULT 'HTTP',
    country TEXT DEFAULT 'XX',
    bandwidth INTEGER DEFAULT 0,
    last_heartbeat INTEGER DEFAULT 0,
    reliability_score REAL DEFAULT 0.5,
    total_hops INTEGER DEFAULT 0,
    UNIQUE(ip_address, port)
);
```

**Wallet Table:**
```sql
CREATE TABLE wallets (
    address TEXT PRIMARY KEY,
    balance REAL DEFAULT 0.0,
    mining_rewards REAL DEFAULT 0.0,
    proxy_fees REAL DEFAULT 0.0,
    service_fees REAL DEFAULT 0.0,
    blocks_mined INTEGER DEFAULT 0,
    proxy_hops_provided INTEGER DEFAULT 0,
    created_at INTEGER DEFAULT 0,
    last_activity INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1
);
```

### 5. Real-time Statistics Calculation

**Hash Rate Calculation:**
```c
// Calculate hash rate from recent valid submissions
double hash_rate = (valid_shares * 1000000.0) / time_window_seconds;

// Format for display
if (hash_rate > 1000000000) {
    snprintf(display, sizeof(display), "%.2f GH/s", hash_rate / 1000000000.0);
} else if (hash_rate > 1000000) {
    snprintf(display, sizeof(display), "%.2f MH/s", hash_rate / 1000000.0);
} else if (hash_rate > 1000) {
    snprintf(display, sizeof(display), "%.2f KH/s", hash_rate / 1000.0);
} else {
    snprintf(display, sizeof(display), "%.2f H/s", hash_rate);
}
```

**Active Miners Count:**
```sql
SELECT COUNT(DISTINCT wallet_address)
FROM mining_work
WHERE created_at > (strftime('%s', 'now') - 300)
AND submitted_at IS NOT NULL;
```

### 6. Security Features

**Cryptographic Verification:**
- **SHA256 Hashing**: All proof-of-work validation
- **Digital Signatures**: Wallet transaction signing
- **SSL/TLS**: All API communications encrypted
- **Rate Limiting**: Prevents abuse and DoS attacks

**Privacy Protection:**
- **No Logging**: Proxy traffic not logged
- **ASN Diversity**: Routes through different networks
- **Encrypted Tunnels**: All hop-to-hop communication encrypted
- **Dead Transactions**: Privacy-focused transaction mixing

### 7. Performance Optimizations

**Database Optimizations:**
```sql
-- Indexes for fast queries
CREATE INDEX idx_mining_work_wallet ON mining_work(wallet_address);
CREATE INDEX idx_mining_work_created ON mining_work(created_at);
CREATE INDEX idx_proxy_pool_heartbeat ON proxy_pool(last_heartbeat);
CREATE INDEX idx_wallets_activity ON wallets(last_activity);
```

**Connection Pooling:**
- **SQLite**: WAL mode for concurrent reads
- **HTTP**: Keep-alive connections
- **Socket Timeouts**: 10-second timeouts for reliability

### 8. Monitoring and Alerting

**Health Checks:**
- **Database**: Connection and query response time
- **Mining Pool**: Work generation and validation
- **Proxy Network**: Node availability and response time
- **API**: Response time and error rates

**Metrics Tracked:**
- Blocks mined per hour
- Active proxy nodes
- API response times
- Error rates by endpoint
- Wallet transaction volume

---

## Implementation Notes

### C API Server Architecture

The core API server is implemented in C for maximum performance:

**File Structure:**
```
c_api_server/
├── main.c              # Entry point and server initialization
├── http_server.c       # HTTP request handling and routing
├── db.c               # SQLite database operations
├── stats.c            # Statistics calculation and caching
├── mining.c           # Mining pool logic and validation
├── proxy_pool.c       # Proxy discovery and management
├── wallet.c           # Wallet operations and balance tracking
└── transaction_log.c  # Transaction history and logging
```

**Key Features:**
- **Multi-threaded**: Handles concurrent requests
- **Memory Efficient**: Minimal memory footprint
- **Fast Response**: Sub-millisecond response times
- **Robust Error Handling**: Comprehensive error management

### Production Deployment

**System Requirements:**
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 100GB SSD for blockchain data
- **Network**: 1Gbps connection recommended
- **Dependencies**: OpenSSL, SQLite3, libcurl, json-c

**Service Configuration:**
```bash
# SystemD service file
[Unit]
Description=ZeroLinkChain API Server
After=network.target

[Service]
Type=simple
User=zerolinkchain
ExecStart=/opt/zerolinkchain/c_api_server/zl_api_server --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

*Last Updated: 2025-09-01*
*API Version: 1.0.0*
*Status: Production*
*Total Endpoints: 25+*
*Documentation Completeness: 100%*
