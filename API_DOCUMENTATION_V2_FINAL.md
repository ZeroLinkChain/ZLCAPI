# ZeroLinkChain API Documentation v2.0

## Overview
The ZeroLinkChain API provides access to wallet operations, 1-on-1 ChainChat messaging, ChainProx VPN services, ChainStore marketplace, and blockchain data. All endpoints are accessed via HTTPS to `zerolinkchain.com`.

## Base URL
```
https://zerolinkchain.com/api.php
```

## Authentication
- **ChainChat**: Requires wallet balance for both participants
- **ChainProx VPN**: Requires mining contribution (public key)
- **ChainStore**: Requires wallet address for fee payments
- **Wallet Operations**: Session token-based (secure) or address-based (legacy) authentication

## Access Control Model

### 🔐 ChainChat (1-on-1 Wallet Chat Only)
- **Type**: Direct wallet-to-wallet messaging
- **Requirement**: Both wallets must have balance
- **No Group Rooms**: Only supports 2-party encrypted conversations
- **Authentication**: Mutual wallet verification

### 🔒 ChainProx VPN  
- **Type**: Anonymous VPN service
- **Requirement**: Mining contribution for bandwidth allocation
- **Bandwidth**: 1 Mbps per 10 H/s mining rate (max 100 Mbps)

### 🏪 ChainStore
- **Type**: Decentralized marketplace and file storage
- **Requirement**: Pay-per-transaction fees
- **Access**: Always available with wallet address

---

## 💬 ChainChat API (1-on-1 Only)

### Check Chat Access
Verify if two wallets can establish a 1-on-1 chat session.

**Endpoint:** `GET /api.php?e=chainchat_access`

**Request:**
```bash
curl -X POST "https://zerolinkchain.com/api.php?e=chainchat_access" \
  -d "wallet_address=YOUR_WALLET_ADDRESS" \
  -d "target_wallet=TARGET_WALLET_ADDRESS"
```

**Response (Success):**
```json
{
  "access": true,
  "message": "ChainChat 1-on-1 session authorized",
  "chat_type": "direct_wallet_to_wallet",
  "participants": ["wallet1", "wallet2"],
  "features": ["direct_messaging", "file_sharing", "encrypted_chat"]
}
```

**Response (Error):**
```json
{
  "error": "Your wallet requires balance for ChainChat",
  "access": false,
  "requirement": "Deposit any amount to your wallet to access ChainChat"
}
```

### Establish Chat Connection
Create a secure 1-on-1 chat session between two wallets.

**Endpoint:** `POST /api.php?e=chainchat_connect`

**Request:**
```bash
curl -X POST "https://zerolinkchain.com/api.php?e=chainchat_connect" \
  -d "wallet_address=YOUR_WALLET_ADDRESS" \
  -d "target_wallet=TARGET_WALLET_ADDRESS"
```

**Response:**
```json
{
  "connected": true,
  "session_id": "chat_16e9ccdad30d319702ca09a50687307ae99d49e3",
  "participants": ["wallet1", "wallet2"],
  "message": "Direct chat established between wallets",
  "encryption": "end_to_end"
}
```

### Send Message
Send an encrypted message in a 1-on-1 chat session.

**Endpoint:** `POST /api.php?e=chainchat_send`

**Request:**
```bash
curl -X POST "https://zerolinkchain.com/api.php?e=chainchat_send" \
  -d "wallet_address=YOUR_WALLET_ADDRESS" \
  -d "target_wallet=TARGET_WALLET_ADDRESS" \
  -d "message=Hello, this is a secure message!" \
  -d "session_id=chat_16e9ccdad30d319702ca09a50687307ae99d49e3"
```

**Response:**
```json
{
  "sent": true,
  "message_id": "msg_a1b2c3d4e5f6789",
  "timestamp": 1693612800,
  "from": "your_wallet_address",
  "to": "target_wallet_address",
  "encrypted": true
}
```

### Receive Messages
Retrieve messages from a 1-on-1 chat session.

**Endpoint:** `POST /api.php?e=chainchat_receive`

**Request:**
```bash
curl -X POST "https://zerolinkchain.com/api.php?e=chainchat_receive" \
  -d "wallet_address=YOUR_WALLET_ADDRESS" \
  -d "session_id=chat_16e9ccdad30d319702ca09a50687307ae99d49e3"
```

**Response:**
```json
{
  "messages": [
    {
      "message_id": "msg_001",
      "from": "other_wallet_address",
      "to": "your_wallet_address",
      "content": "Hello! This is a test message.",
      "timestamp": 1693612500,
      "encrypted": true
    }
  ],
  "session_id": "chat_16e9ccdad30d319702ca09a50687307ae99d49e3",
  "unread_count": 1
}
```

---

## � Secure Wallet Sessions

ZeroLinkChain implements secure session-based wallet authentication to eliminate the need for repeated private key transmission. When importing or creating wallets, the API returns a secure session token that can be used for subsequent operations.

### Session Authentication Benefits
- **🔒 Enhanced Security**: Private keys never stored client-side or transmitted repeatedly
- **⏱️ Time-Limited Access**: Sessions expire after 24 hours
- **🔑 Token-Based Auth**: 256-bit secure session tokens for wallet operations
- **🛡️ Server-Side Storage**: Private keys temporarily encrypted server-side

### Session Flow
1. **Import/Create Wallet** → Receive session token + wallet details
2. **Store Session Token** → Client stores token (not private key)
3. **Use Token for Operations** → Balance, send, history via session token
4. **Automatic Expiry** → Session expires after 24 hours, re-import required

---

## �💰 Wallet API

### Create New Wallet
Generate a new wallet with private key and session token.

**Endpoint:** `GET /api.php?e=wallet_create`

**Request:**
```bash
curl "https://zerolinkchain.com/api.php?e=wallet_create"
```

**Response:**
```json
{
  "address": "zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8",
  "private_key": "a1b2c3d4e5f6789...",
  "session_token": "2cae75f5c41362863861ef15748e8cf9ee098855f8b0c729fbbd2022f858358e",
  "status": "created",
  "expires_in": 86400
}
```

⚠️ **Important**: Save the `private_key` securely - it's only returned once. Use `session_token` for subsequent operations.

### Create Wallet with Mnemonic
Generate a new wallet with mnemonic phrase.

**Endpoint:** `GET /api.php?e=wallet_mnemonic_create`

**Request:**
```bash
curl "https://zerolinkchain.com/api.php?e=wallet_mnemonic_create"
```

**Response:**
```json
{
  "address": "zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8",
  "mnemonic": "abandon ability able about above absent absorb abstract absurd abuse access accident",
  "private_key": "a1b2c3d4e5f6789...",
  "session_token": "3dbe86f6d52473974d72ae26859f0284fe119966g9c1d840gced3033g969469f",
  "status": "created",
  "expires_in": 86400
}
```

⚠️ **Important**: Save both `mnemonic` and `private_key` securely - they're only returned once. Use `session_token` for subsequent operations.

### Import Wallet from Mnemonic
Import an existing wallet using mnemonic phrase and receive secure session token.

**Endpoint:** `POST /api.php?e=wallet_mnemonic_import`

**Request:**
```bash
curl -X POST "https://zerolinkchain.com/api.php?e=wallet_mnemonic_import" \
  -d "mnemonic=abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid"
```

**Response:**
```json
{
  "address": "zlc3b98dcd8570951414b02261dbd361be251e68a",
  "mnemonic": "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid",
  "session_token": "4eff97g7e63584085e83bg37960g1395gg230877h0d2e951hdfee4044h080580g",
  "status": "imported",
  "expires_in": 86400
}
```

### Import Wallet from Private Key
Import an existing wallet using private key and receive secure session token.

**Endpoint:** `POST /api.php?e=wallet_import`

**Request:**
```bash
curl -X POST "https://zerolinkchain.com/api.php?e=wallet_import" \
  -d "privateKey=ac1f16a6eeccbddd013b1f1f5142429c3e631c65c7eb211ffe8052099ae7019e"
```

**Response:**
```json
{
  "address": "zlc3b98dcd8570951414b02261dbd361be251e68a",
  "session_token": "2cae75f5c41362863861ef15748e8cf9ee098855f8b0c729fbbd2022f858358e",
  "status": "imported",
  "expires_in": 86400
}
```

### Check Wallet Balance
Get the current balance using either wallet address (legacy) or session token (secure).

**Endpoint:** `POST /api.php?e=wallet_balance`

**Secure Method (Recommended):**
```bash
curl -X POST "https://zerolinkchain.com/api.php?e=wallet_balance" \
  -d "session_token=2cae75f5c41362863861ef15748e8cf9ee098855f8b0c729fbbd2022f858358e"
```

**Legacy Method:**
```bash
curl -X POST "https://zerolinkchain.com/api.php?e=wallet_balance" \
  -d "address=zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8"
```

**Response:**
```json
{
  "address": "zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8",
  "balance": "12.34567890",
  "currency": "ZLC"
}
```

### Verify Session Token
Validate if a session token is still active and get session info.

**Endpoint:** `POST /api.php?e=wallet_session_verify`

**Request:**
```bash
curl -X POST "https://zerolinkchain.com/api.php?e=wallet_session_verify" \
  -d "session_token=2cae75f5c41362863861ef15748e8cf9ee098855f8b0c729fbbd2022f858358e"
```

**Response (Valid Session):**
```json
{
  "valid": true,
  "address": "zlc3b98dcd8570951414b02261dbd361be251e68a",
  "expires_in": 82400
}
```

**Response (Invalid/Expired Session):**
```json
{
  "valid": false,
  "error": "Invalid or expired session"
}
```

### Get Session Information
Get detailed information about a session token.

**Endpoint:** `POST /api.php?e=wallet_session_info`

**Request:**
```bash
curl -X POST "https://zerolinkchain.com/api.php?e=wallet_session_info" \
  -d "session_token=2cae75f5c41362863861ef15748e8cf9ee098855f8b0c729fbbd2022f858358e"
```

**Response:**
```json
{
  "address": "zlc3b98dcd8570951414b02261dbd361be251e68a",
  "created": 1725241320,
  "expires": 1725327720,
  "expires_in": 82400,
  "last_used": 1725245200
}
```

### Send Transaction
Send ZLC to another wallet using secure session token (recommended) or private key (legacy).

**Endpoint:** `POST /api.php?e=wallet_send`

**Secure Method (Recommended):**
```bash
curl -X POST "https://zerolinkchain.com/api.php?e=wallet_send" \
  -d "session_token=2cae75f5c41362863861ef15748e8cf9ee098855f8b0c729fbbd2022f858358e" \
  -d "to=RECIPIENT_ADDRESS" \
  -d "amount=1.5"
```

**Legacy Method:**
```bash
curl -X POST "https://zerolinkchain.com/api.php?e=wallet_send" \
  -d "from=YOUR_WALLET_ADDRESS" \
  -d "to=RECIPIENT_ADDRESS" \
  -d "amount=1.5" \
  -d "privateKey=YOUR_PRIVATE_KEY"
```

**Response:**
```json
{
  "txid": "tx_a1b2c3d4e5f6789",
  "status": "pending",
  "message": "Transaction submitted to network"
}
```

### Transaction History
Get transaction history for a wallet address.

**Endpoint:** `POST /api.php?e=wallet_history`

**Request:**
```bash
curl -X POST "https://zerolinkchain.com/api.php?e=wallet_history" \
  -d "address=zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8"
```

**Response:**
```json
{
  "transactions": [
    {
      "txid": "tx_001",
      "type": "received",
      "amount": "5.0",
      "timestamp": 1693609200
    },
    {
      "txid": "tx_002",
      "type": "sent",
      "amount": "-1.5",
      "timestamp": 1693605600
    }
  ]
}
```

---

## 🔒 ChainProx VPN API

### Check VPN Access
Verify mining contribution for VPN bandwidth allocation.

**Endpoint:** `POST /api.php?e=chainprox_access`

**Request:**
```bash
curl -X POST "https://zerolinkchain.com/api.php?e=chainprox_access" \
  -d "public_key=YOUR_MINING_PUBLIC_KEY"
```

**Response:**
```json
{
  "access": true,
  "message": "ChainProx VPN access granted",
  "bandwidth_mbps": 15.05,
  "mining_rate": 150.5,
  "available_nodes": 45
}
```

---

## 🏪 ChainStore API

### Check Store Access
Verify wallet address for marketplace transactions.

**Endpoint:** `POST /api.php?e=chainstore_access`

**Request:**
```bash
curl -X POST "https://zerolinkchain.com/api.php?e=chainstore_access" \
  -d "wallet_address=YOUR_WALLET_ADDRESS"
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

---

## 📊 Network Data API

### Network Statistics
Get current network statistics.

**Endpoint:** `GET /api.php?e=stats`

**Request:**
```bash
curl "https://zerolinkchain.com/api.php?e=stats"
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
Get mining pool statistics.

**Endpoint:** `GET /api.php?e=mining`

**Request:**
```bash
curl "https://zerolinkchain.com/api.php?e=mining"
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

### VPN Network Data
Get VPN node information.

**Endpoint:** `GET /api.php?e=vpn`

**Request:**
```bash
curl "https://zerolinkchain.com/api.php?e=vpn"
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

---

## Error Handling

### Common Error Responses

**Invalid Endpoint:**
```json
{
  "error": "Invalid endpoint"
}
```

**Missing Parameters:**
```json
{
  "error": "Wallet address required",
  "access": false
}
```

**Insufficient Balance:**
```json
{
  "error": "Your wallet requires balance for ChainChat",
  "access": false,
  "requirement": "Deposit any amount to your wallet to access ChainChat"
}
```

**Server Error:**
```json
{
  "error": "Internal server error",
  "detail": "Error description"
}
```

---

## Rate Limits
- **Wallet Operations**: 100 requests per minute
- **ChainChat Messages**: 50 messages per minute per session
- **Network Data**: 1000 requests per minute

## Security Notes
- All ChainChat messages are end-to-end encrypted
- Private keys are never stored on the server
- Wallet addresses are used for authentication
- Session IDs are cryptographically generated
- All API calls use HTTPS encryption

---

*Last Updated: September 2, 2025 - API Version 2.0*
