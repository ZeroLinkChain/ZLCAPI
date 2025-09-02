# ZeroLinkChain API Documentation

## Overview

The ZeroLinkChain API provides access to wallet operations, network features, and secure communication services. All endpoints follow RESTful principles and return JSON responses.

**Base URL:** `https://zerolinkchain.com/api.php`  
**Authentication:** Session-based for ChainChat, balance-based for features  
**Rate Limiting:** Implemented for security

## Access Control Model

### ChainChat - Mutual Authentication Required
- **Requirement:** Both parties must have wallet balance
- **Process:** Mutual wallet authentication via cryptographic signatures  
- **Security:** End-to-end encryption with wallet-based identity verification
- **Connection:** Requires target wallet address for secure channel establishment

### ChainProx VPN - Contribution Based
- **Requirement:** Active mining contribution
- **Bandwidth:** Allocated proportionally to mining rate (1 Mbps per 10 H/s)
- **Access:** Continuous based on network contribution

### ChainStore - Fee Based  
- **Model:** Pay-per-transaction micro-payments
- **Fees:** 0.001 ZLC/MB upload, 0.0001 ZLC/file download
- **Access:** Immediate with sufficient wallet balance

## Wallet Endpoints

### Create New Wallet
```
POST /api.php?e=wallet_create
```

**Response:**
```json
{
  "address": "zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8",
  "privateKey": "afe82c57d21aaddd24490d9721eac49f978d04f6928841958c540a7d4c63a42b",
  "status": "created"
}
```

### Create Wallet with Mnemonic
```
POST /api.php?e=wallet_mnemonic_create
```

**Response:**
```json
{
  "address": "zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8",
  "mnemonic": "abandon ability able about above absent absorb abstract absurd abuse access accident",
  "privateKey": "afe82c57d21aaddd24490d9721eac49f978d04f6928841958c540a7d4c63a42b",
  "status": "created"
}
```

### Import Wallet from Private Key
```
POST /api.php?e=wallet_import
Content-Type: application/x-www-form-urlencoded

privateKey=afe82c57d21aaddd24490d9721eac49f978d04f6928841958c540a7d4c63a42b
```

**Response:**
```json
{
  "address": "zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8",
  "status": "imported"
}
```

### Import Wallet from Mnemonic
```
POST /api.php?e=wallet_mnemonic_import
Content-Type: application/x-www-form-urlencoded

mnemonic=abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid
```

**Response:**
```json
{
  "address": "zlc3b98dcd8570951414b02261dbd361be251e68a",
  "privateKey": "ac1f16a6eeccbddd013b1f1f5142429c3e631c65c7eb211ffe8052099ae7019e",
  "status": "imported"
}
```

### Check Wallet Balance
```
POST /api.php?e=wallet_balance
Content-Type: application/x-www-form-urlencoded

address=zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8
```

**Response:**
```json
{
  "address": "zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8",
  "balance": "12.34567890",
  "currency": "ZLC"
}
```

### Send Transaction
```
POST /api.php?e=wallet_send
Content-Type: application/x-www-form-urlencoded

from=zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8
to=zlc3b98dcd8570951414b02261dbd361be251e68a
amount=1.5
fee=0.001
```

**Response:**
```json
{
  "txid": "tx_a1b2c3d4e5f6g7h8",
  "status": "pending",
  "message": "Transaction submitted to network"
}
```

### Transaction History
```
POST /api.php?e=wallet_history
Content-Type: application/x-www-form-urlencoded

address=zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8
```

**Response:**
```json
{
  "transactions": [
    {
      "txid": "tx_001",
      "type": "received",
      "amount": "5.0",
      "timestamp": 1693612800
    },
    {
      "txid": "tx_002",
      "type": "sent", 
      "amount": "-1.5",
      "timestamp": 1693609200
    }
  ]
}
```

## ChainChat Endpoints - Mutual Authentication

### Check ChainChat Access
```
POST /api.php?e=chainchat_access
Content-Type: application/x-www-form-urlencoded

wallet_address=zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8
target_address=zlc3b98dcd8570951414b02261dbd361be251e68a
```

**Response (Success):**
```json
{
  "access": true,
  "message": "ChainChat mutual authentication available",
  "your_address": "zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8",
  "target_address": "zlc3b98dcd8570951414b02261dbd361be251e68a",
  "auth_challenge": "a1b2c3d4e5f6g7h8",
  "features": ["secure_messaging", "mutual_auth", "encrypted_channel"],
  "next_step": "Both parties must confirm authentication challenge"
}
```

**Response (Error - No Target):**
```json
{
  "error": "ChainChat requires connection to another wallet address",
  "access": false,
  "requirement": "Specify target wallet address for mutual authentication"
}
```

### Initiate ChainChat Connection
```
POST /api.php?e=chainchat_connect
Content-Type: application/x-www-form-urlencoded

wallet_address=zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8
target_address=zlc3b98dcd8570951414b02261dbd361be251e68a
```

**Response:**
```json
{
  "status": "connection_initiated",
  "session_id": "chat_a1b2c3d4",
  "auth_token": "e5f6g7h8i9j0k1l2",
  "your_address": "zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8",
  "target_address": "zlc3b98dcd8570951414b02261dbd361be251e68a",
  "message": "Mutual authentication required - both parties must confirm",
  "expires_in": 300
}
```

### Authenticate ChainChat Session
```
POST /api.php?e=chainchat_auth
Content-Type: application/x-www-form-urlencoded

session_id=chat_a1b2c3d4
auth_token=e5f6g7h8i9j0k1l2
wallet_address=zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8
signature=3045022100a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z602201f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a1b2c3d4e5
```

**Response:**
```json
{
  "status": "authenticated",
  "session_id": "chat_a1b2c3d4",
  "wallet_address": "zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8",
  "chat_enabled": true,
  "message": "Mutual authentication successful - secure chat channel established",
  "features": ["encrypted_messaging", "file_transfer", "voice_call"]
}
```

## ChainStore Endpoints

### Check ChainStore Access
```
POST /api.php?e=chainstore_access
Content-Type: application/x-www-form-urlencoded

wallet_address=zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8
```

**Response:**
```json
{
  "access": true,
  "message": "ChainStore access available",
  "fee_structure": {
    "upload_fee": "0.001 ZLC per MB",
    "download_fee": "0.0001 ZLC per file",
    "listing_fee": "0.01 ZLC per item"
  },
  "features": ["marketplace", "file_storage", "smart_contracts"]
}
```

## ChainProx VPN Endpoints

### Check ChainProx Access
```
POST /api.php?e=chainprox_access
Content-Type: application/x-www-form-urlencoded

public_key=test_miner_001
```

**Response (Success):**
```json
{
  "access": true,
  "message": "ChainProx VPN access granted",
  "bandwidth_mbps": 15.05,
  "mining_rate": 150.5,
  "available_nodes": 45
}
```

**Response (No Contribution):**
```json
{
  "error": "ChainProx requires network contribution",
  "access": false,
  "requirement": "Start mining or hosting to earn VPN bandwidth allocation"
}
```

## Network Information Endpoints

### Network Statistics
```
GET /api.php?e=stats
```

**Response:**
```json
{
  "network_hash_rate": "1.23 TH/s",
  "difficulty": 1234567.89,
  "block_height": 95847,
  "active_nodes": 156,
  "total_supply": "21000000 ZLC"
}
```

### Mining Pool Data
```
GET /api.php?e=mining
```

**Response:**
```json
{
  "pool_hash_rate": "456.78 GH/s",
  "miners_online": 89,
  "blocks_found_24h": 12,
  "estimated_earnings": "0.0034 ZLC/day per GH/s"
}
```

### VPN Network Status
```
GET /api.php?e=vpn
```

**Response:**
```json
{
  "active_nodes": 45,
  "total_bandwidth": "2.1 Gbps",
  "countries": 23,
  "avg_latency": "45ms"
}
```

### Blockchain Status
```
GET /api.php?e=blockchain
```

**Response:**
```json
{
  "status": "synced",
  "block_height": 95847,
  "last_block_time": 1693612800,
  "sync_progress": 100.0
}
```

## Error Responses

### Standard Error Format
```json
{
  "error": "Error message description",
  "code": "ERROR_CODE",
  "details": "Additional error information"
}
```

### Common Error Codes
- `INVALID_ENDPOINT` - Endpoint not found or not allowed
- `MISSING_PARAMETERS` - Required parameters not provided
- `INVALID_ADDRESS` - Wallet address format invalid
- `INSUFFICIENT_BALANCE` - Not enough funds for operation
- `AUTHENTICATION_FAILED` - ChainChat authentication failed
- `NO_CONTRIBUTION` - Mining contribution required for VPN access
- `UPSTREAM_ERROR` - Backend service unavailable

## Rate Limiting

- **Wallet Operations:** 100 requests per minute per IP
- **ChainChat:** 50 requests per minute per wallet address
- **Network Data:** 200 requests per minute per IP
- **VPN Access:** 20 requests per minute per public key

## Security Notes

### ChainChat Security Model
1. **Mutual Authentication:** Both parties must have wallet balance and valid signatures
2. **End-to-End Encryption:** Messages encrypted with wallet-derived keys
3. **Session Expiry:** Authentication sessions expire in 5 minutes
4. **Anti-Spam:** Balance requirement prevents spam and abuse

### Wallet Security
1. **Private Key Protection:** Never transmitted or stored on server
2. **Address Derivation:** Deterministic generation from private keys
3. **Signature Verification:** All transactions require valid signatures
4. **Secure Communication:** All API calls over HTTPS

### VPN Security
1. **Contribution Verification:** Mining rate verified through public key
2. **Bandwidth Allocation:** Fair distribution based on contribution
3. **Node Selection:** Automatic selection of optimal exit nodes
4. **Traffic Encryption:** All VPN traffic encrypted end-to-end

---

**Last Updated:** September 2, 2025  
**API Version:** 2.0  
**Documentation Version:** 1.3
