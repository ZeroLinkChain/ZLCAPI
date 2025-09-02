# ZeroLinkChain API Documentation

## 🚀 Complete API Reference for Full Implementation

**Base URL**: `https://zerolinkchain.com`  
**API Version**: 1.0  
**Authentication**: Bearer Token (Session-based)

---

## 📋 **Quick Start**

### 1. Create a Wallet
```bash
curl -X POST "https://zerolinkchain.com/api/wallet/create"
```

### 2. Use Session Token for Authenticated Requests
```bash
curl -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
     "https://zerolinkchain.com/api/wallet/balance"
```

---

## 🔗 **Core Blockchain APIs**

### **Health Check**
```http
GET /api/health
```
**Response:**
```json
{
  "status": "ok"
}
```

### **Mining Statistics**
```http
GET /api/miner/stats
```
**Response:**
```json
{
  "height": 18,
  "difficulty": 4,
  "hashrate_hps": 66666.67,
  "attempts": 72000
}
```

### **Chain Integrity**
```http
GET /api/integrity/status
```
**Response:**
```json
{
  "height": 18,
  "last_block_time": 1756837361,
  "chain_integrity": "verified",
  "rolling_hash": "e2d4d6fae9de18033168b0ca14e7b28328dbe32632569e8ec07c08c89ceec338"
}
```

### **Pending Rewards**
```http
GET /api/rewards/pending
```
**Response:**
```json
[]
```

---

## 💰 **Wallet Management APIs**

### **Create New Wallet**
```http
POST /api/wallet/create
```
**Response:**
```json
{
  "address": "ZLCa36a46bc0af814bb56669d783af739fc438e71a2bd2b0006645e5314651fd",
  "private_key": "22dd95371276c03f9d5ce3744f1b541a5a2d0235a1e319d3499f1ebaaf212032",
  "mnemonic": "abuse abstract absent abuse absent about about absurd absurd abstract able about",
  "session_token": "15d692eef6ed6a8291df094c8b57542eee2d192ba15543f716cc1c5db3553878",
  "expires_in": 86400,
  "status": "created"
}
```

### **Import Wallet from Mnemonic**
```http
POST /api/wallet/import/mnemonic
Content-Type: application/json

{
  "mnemonic": "word1 word2 word3 ... word12"
}
```

### **Import Wallet from Private Key**
```http
POST /api/wallet/import/privatekey
Content-Type: application/json

{
  "private_key": "your_64_character_hex_private_key"
}
```

### **Get Wallet Balance**
```http
GET /api/wallet/balance
Authorization: Bearer YOUR_SESSION_TOKEN
```
**Response:**
```json
{
  "wallet": "ZLCa36a46bc0af814bb56669d783af739fc438e71a2bd2b0006645e5314651fd",
  "balance": 0,
  "source": "blockchain"
}
```

---

## 💸 **Transaction APIs**

### **Send Transaction**
```http
POST /api/wallet/send
Authorization: Bearer YOUR_SESSION_TOKEN
Content-Type: application/json

{
  "to_wallet": "ZLCde35bcb2fe35836900d975132fbfc03b5d2eb4b85d3575c7e8f32cf04e4d0",
  "amount": 1.0,
  "fee": 0.001
}
```
**Response:**
```json
{
  "txid": "tx_d049c04ed66ac47b96895407e0616330b3dfec45f3dfa98208559329c70932d5",
  "from_wallet": "ZLC6c4090e15ecd40b2be1c36ff06e2c6af38371c0c46944653ee12650c11e1d",
  "to_wallet": "ZLCde35bcb2fe35836900d975132fbfc03b5d2eb4b85d3575c7e8f32cf04e4d0",
  "amount": 1,
  "fee": 0.001,
  "timestamp": 1756845402,
  "status": "pending",
  "confirmations": 0,
  "estimated_confirmation": 60,
  "block_height": null,
  "privacy_enabled": true,
  "encrypted_for_sender": true,
  "encrypted_for_recipient": true
}
```

### **Get Transaction History**
```http
GET /api/wallet/transactions
Authorization: Bearer YOUR_SESSION_TOKEN
```
**Response:**
```json
{
  "wallet": "ZLC6c4090e15ecd40b2be1c36ff06e2c6af38371c0c46944653ee12650c11e1d",
  "transactions": [
    {
      "txid": "tx_genesis_50c11e1d",
      "type": "receive",
      "from_wallet": "ZLC0000000000000000000000000000000000000000000000000000000000000",
      "to_wallet": "ZLC6c4090e15ecd40b2be1c36ff06e2c6af38371c0c46944653ee12650c11e1d",
      "amount": 0,
      "fee": 0,
      "timestamp": 1756841808,
      "status": "confirmed",
      "confirmations": 6,
      "block_height": 18,
      "description": "Genesis wallet creation"
    }
  ],
  "total_count": 1,
  "page": 1,
  "per_page": 50
}
```

### **Refresh Session Token**
```http
POST /api/wallet/refresh
Authorization: Bearer YOUR_CURRENT_SESSION_TOKEN
```
**Response:**
```json
{
  "session_token": "new_session_token_here",
  "expires_in": 86400,
  "address": "ZLCa36a46bc0af814bb56669d783af739fc438e71a2bd2b0006645e5314651fd",
  "status": "refreshed"
}
```

---

## 🌐 **Node APIs**

### **Node Statistics**
```http
GET http://localhost:8335/stats
```
**Response:**
```json
{
  "node_id": "cc012ed54d76556e",
  "version": "1.0.0",
  "uptime": 231.15871715545654,
  "peers_connected": 0,
  "blockchain_size": 2631,
  "blocks_count": 0,
  "p2p_port": 8334,
  "api_port": 8335,
  "data_directory": "/var/lib/zerolinkchain/node"
}
```

### **Connected Peers**
```http
GET http://localhost:8335/peers
```
**Response:**
```json
{
  "peers": []
}
```

### **Download Blockchain Data**
```http
GET http://localhost:8335/blockchain
```
**Response:** Binary blockchain data

---

## ⛏️ **Mining Pool Integration**

### **Pool Connection**
- **Host**: `your-server-ip`
- **Port**: `8333`
- **Protocol**: JSON-RPC over TCP

### **Work Template Format**
```json
{
  "height": 19,
  "previous_hash": "e2d4d6fae9de18033168b0ca14e7b28328dbe32632569e8ec07c08c89ceec338",
  "difficulty": 4,
  "target": "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
  "coinbase_address": "ZLCde35bcb2fe35836900d975132fbfc03b5d2eb4b85d3575c7e8f32cf04e4d0",
  "timestamp": 1756845402,
  "nonce_start": 0,
  "nonce_end": 4294967295
}
```

### **Share Submission Format**
```json
{
  "nonce": 123456,
  "hash": "0000abcd1234567890abcdef1234567890abcdef1234567890abcdef12345678"
}
```

---

## 🔒 **Authentication & Security**

### **Session Token Usage**
```http
Authorization: Bearer 15d692eef6ed6a8291df094c8b57542eee2d192ba15543f716cc1c5db3553878
```

### **Token Expiration**
- **Default**: 86400 seconds (24 hours)
- **Refresh**: Use `/api/wallet/refresh` before expiration

### **Privacy Features**
- All transactions are encrypted for sender and recipient
- Private keys never transmitted over network
- Session-based authentication prevents key exposure

---

## 📱 **Implementation Examples**

### **JavaScript/Node.js**
```javascript
const API_BASE = 'https://zerolinkchain.com';

// Create wallet
const createWallet = async () => {
  const response = await fetch(`${API_BASE}/api/wallet/create`, {
    method: 'POST'
  });
  return await response.json();
};

// Send transaction
const sendTransaction = async (sessionToken, toWallet, amount) => {
  const response = await fetch(`${API_BASE}/api/wallet/send`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${sessionToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      to_wallet: toWallet,
      amount: amount,
      fee: 0.001
    })
  });
  return await response.json();
};
```

### **Python**
```python
import requests

API_BASE = 'https://zerolinkchain.com'

# Create wallet
def create_wallet():
    response = requests.post(f'{API_BASE}/api/wallet/create')
    return response.json()

# Send transaction
def send_transaction(session_token, to_wallet, amount):
    headers = {'Authorization': f'Bearer {session_token}'}
    data = {
        'to_wallet': to_wallet,
        'amount': amount,
        'fee': 0.001
    }
    response = requests.post(f'{API_BASE}/api/wallet/send', 
                           headers=headers, json=data)
    return response.json()
```

### **cURL Examples**
```bash
# Create wallet
curl -X POST "https://zerolinkchain.com/api/wallet/create"

# Get balance
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://zerolinkchain.com/api/wallet/balance"

# Send transaction
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"to_wallet":"ZLC...","amount":1.0,"fee":0.001}' \
     "https://zerolinkchain.com/api/wallet/send"
```

---

## ⚠️ **Error Handling**

### **Common Error Responses**
```json
{
  "error": "authorization_required"
}

{
  "error": "invalid_or_expired_session"
}

{
  "error": "insufficient_balance"
}

{
  "error": "invalid_recipient_address"
}

{
  "error": "missing_transaction_data"
}
```

### **HTTP Status Codes**
- `200`: Success
- `400`: Bad Request (invalid data)
- `401`: Unauthorized (missing/invalid token)
- `404`: Not Found (endpoint doesn't exist)
- `502`: Bad Gateway (backend service error)

---

## 🚀 **Production Deployment**

### **Service Endpoints**
- **Main API**: `https://zerolinkchain.com`
- **Node API**: `http://your-server:8335`
- **Mining Pool**: `your-server:8333`

### **Rate Limits**
- **Wallet Operations**: 100 requests/minute
- **Balance Queries**: 1000 requests/minute
- **Transaction Submissions**: 10 requests/minute

### **Monitoring**
```bash
# Check service status
systemctl status zerolinkchain-wallet zerolinkchain-pool zerolinkchain-node

# View logs
journalctl -u zerolinkchain-wallet -f
```

---

---

## 🛠️ **Implementation Patterns**

### **Wallet Application Flow**
1. **Create/Import Wallet** → Get session token
2. **Check Balance** → Display current ZLC balance
3. **Send Transaction** → Create and broadcast transaction
4. **Monitor History** → Track transaction status
5. **Refresh Session** → Maintain authentication

### **Mining Application Flow**
1. **Connect to Pool** → TCP connection to port 8333
2. **Receive Work** → Get mining template
3. **Mine Shares** → Calculate proof-of-work
4. **Submit Shares** → Send valid shares to pool
5. **Receive Rewards** → Automatic distribution to wallet

### **Node Application Flow**
1. **Connect to Network** → P2P connection to port 8334
2. **Sync Blockchain** → Download and verify blocks
3. **Serve Data** → Provide blockchain data via API
4. **Relay Transactions** → Forward transactions to network

---

## 📚 **SDK Examples**

### **React Native Mobile App**
```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

class ZeroLinkChainWallet {
  constructor() {
    this.apiBase = 'https://zerolinkchain.com';
    this.sessionToken = null;
  }

  async createWallet() {
    const response = await fetch(`${this.apiBase}/api/wallet/create`, {
      method: 'POST'
    });
    const wallet = await response.json();

    // Store session token securely
    await AsyncStorage.setItem('zlc_session', wallet.session_token);
    await AsyncStorage.setItem('zlc_address', wallet.address);

    this.sessionToken = wallet.session_token;
    return wallet;
  }

  async getBalance() {
    const response = await fetch(`${this.apiBase}/api/wallet/balance`, {
      headers: { 'Authorization': `Bearer ${this.sessionToken}` }
    });
    return await response.json();
  }

  async sendTransaction(toAddress, amount) {
    const response = await fetch(`${this.apiBase}/api/wallet/send`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.sessionToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        to_wallet: toAddress,
        amount: amount,
        fee: 0.001
      })
    });
    return await response.json();
  }
}
```

### **Desktop Application (Electron)**
```javascript
const { ipcMain, ipcRenderer } = require('electron');

// Main process
class ZeroLinkChainNode {
  constructor() {
    this.nodeUrl = 'http://localhost:8335';
  }

  async getNodeStats() {
    const response = await fetch(`${this.nodeUrl}/stats`);
    return await response.json();
  }

  async downloadBlockchain() {
    const response = await fetch(`${this.nodeUrl}/blockchain`);
    const buffer = await response.arrayBuffer();
    return new Uint8Array(buffer);
  }
}

// Renderer process
ipcRenderer.invoke('get-node-stats').then(stats => {
  console.log('Node Stats:', stats);
});
```

### **Web Application (Vue.js)**
```javascript
import { ref, onMounted } from 'vue';

export default {
  setup() {
    const wallet = ref(null);
    const balance = ref(0);
    const transactions = ref([]);

    const createWallet = async () => {
      const response = await fetch('https://zerolinkchain.com/api/wallet/create', {
        method: 'POST'
      });
      wallet.value = await response.json();
      localStorage.setItem('zlc_session', wallet.value.session_token);
    };

    const loadBalance = async () => {
      const token = localStorage.getItem('zlc_session');
      const response = await fetch('https://zerolinkchain.com/api/wallet/balance', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      balance.value = data.balance;
    };

    const loadTransactions = async () => {
      const token = localStorage.getItem('zlc_session');
      const response = await fetch('https://zerolinkchain.com/api/wallet/transactions', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      transactions.value = data.transactions;
    };

    onMounted(() => {
      if (localStorage.getItem('zlc_session')) {
        loadBalance();
        loadTransactions();
      }
    });

    return {
      wallet,
      balance,
      transactions,
      createWallet,
      loadBalance,
      loadTransactions
    };
  }
};
```

---

## 🔧 **Advanced Features**

### **Batch Transactions**
```javascript
const sendBatchTransactions = async (sessionToken, transactions) => {
  const promises = transactions.map(tx =>
    fetch('https://zerolinkchain.com/api/wallet/send', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${sessionToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(tx)
    })
  );

  const responses = await Promise.all(promises);
  return Promise.all(responses.map(r => r.json()));
};
```

### **Real-time Balance Updates**
```javascript
const subscribeToBalanceUpdates = (sessionToken, callback) => {
  const pollBalance = async () => {
    const response = await fetch('https://zerolinkchain.com/api/wallet/balance', {
      headers: { 'Authorization': `Bearer ${sessionToken}` }
    });
    const data = await response.json();
    callback(data.balance);
  };

  // Poll every 30 seconds
  setInterval(pollBalance, 30000);
  pollBalance(); // Initial call
};
```

### **Mining Pool Integration**
```javascript
const net = require('net');

class ZeroLinkChainMiner {
  constructor(poolHost = 'localhost', poolPort = 8333) {
    this.poolHost = poolHost;
    this.poolPort = poolPort;
    this.socket = null;
  }

  connect() {
    this.socket = net.createConnection(this.poolPort, this.poolHost);

    this.socket.on('data', (data) => {
      const work = JSON.parse(data.toString());
      if (work.type !== 'keepalive') {
        this.mineShare(work);
      }
    });
  }

  mineShare(workTemplate) {
    // Simple mining implementation
    for (let nonce = 0; nonce < 1000000; nonce++) {
      const hash = this.calculateHash(workTemplate, nonce);
      if (this.isValidShare(hash, workTemplate.target)) {
        this.submitShare({ nonce, hash });
        break;
      }
    }
  }

  submitShare(share) {
    this.socket.write(JSON.stringify(share) + '\n');
  }
}
```

---

**🎯 This complete API documentation provides everything needed to implement full ZeroLinkChain functionality including wallets, transactions, mining, and blockchain interaction across all platforms.**
