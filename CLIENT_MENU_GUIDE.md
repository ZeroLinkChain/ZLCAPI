# ZeroLinkChain Client - Menu Interface Guide

## 📱 Background Menu System

The ZeroLinkChain client operates as a **system tray application** that runs continuously in the background, providing instant access to all network features through an intuitive right-click menu.

### 🖥️ System Tray Menu Structure
```
[ZLC Icon] Right-click for menu:
├── 💰 Wallet
│   ├── Create New Wallet
│   ├── Import Wallet (Private Key/Mnemonic)
│   ├── Send Funds
│   ├── Receive Funds
│   └── Transaction History
├── 💬 ChainChat (requires wallet balance)
│   ├── Connect to Wallet Address
│   ├── 1-on-1 Encrypted Chat
│   ├── Send Files Securely
│   └── Message History
├── 🔒 ChainProx VPN (requires mining contribution)
│   ├── Connect VPN
│   ├── Select Country
│   ├── Bandwidth Status
│   └── Node Selection
├── ⛏️ Mining
│   ├── Start/Stop Mining
│   ├── Pool Selection
│   ├── Mining Stats
│   └── Earnings Tracker
├── 🏪 ChainStore (pay-per-transaction)
│   ├── Browse Marketplace
│   ├── Upload Files
│   ├── Smart Contracts
│   └── Transaction Fees
├── ⚙️ Settings
│   ├── Import Keys
│   ├── Network Config
│   ├── Preferences
│   └── About
└── ❌ Exit
```

## 🚀 Quick Start

### 1. Launch Client
```bash
zlc
```
- Client starts in background
- System tray icon appears
- Ready for menu access

### 2. Initial Setup
Right-click system tray icon → Settings → Import Keys
- **Private Key:** For wallet and ChainChat access
- **Public Key:** For mining and VPN bandwidth

### 3. Feature Access
Features unlock automatically based on:
- **ChainChat:** Wallet balance required
- **ChainProx VPN:** Mining contribution required  
- **ChainStore:** Pay-per-transaction
- **Wallet/Mining:** Always available

## 🎯 Menu Features

### 💰 Wallet Menu
- **Create:** Generate new wallet with mnemonic
- **Import:** Restore from private key or mnemonic
- **Send:** Transfer funds with fee estimation
- **Receive:** Generate receiving addresses
- **History:** View transaction history

### 💬 ChainChat Menu (Balance Required)
- **Connect:** Enter target wallet address for 1-on-1 chat
- **Messages:** Direct encrypted messaging
- **Files:** Share files securely between wallets
- **History:** View message history for each wallet connection

### 🔒 ChainProx VPN Menu (Mining Required)
- **Connect:** Quick VPN connection
- **Countries:** Select exit country
- **Bandwidth:** View allocated bandwidth
- **Nodes:** Choose specific VPN nodes

### ⛏️ Mining Menu
- **Start/Stop:** Control mining operation
- **Pool:** Select mining pool
- **Stats:** View hashrate and earnings
- **Tracker:** Monitor daily/monthly earnings

### 🏪 ChainStore Menu (Fee-Based)
- **Browse:** Explore marketplace
- **Upload:** Store files with fees
- **Contracts:** Deploy smart contracts
- **Fees:** View transaction costs

## ⚙️ Settings & Configuration

### Key Management
- Import/export private keys
- Manage public keys
- Backup wallet seeds
- Key security settings

### Network Settings
- API endpoint configuration
- Connection timeouts
- Proxy settings
- Debug logging

### Preferences
- Auto-start options
- Notification settings
- Menu customization
- Feature toggles

---

*The ZeroLinkChain client is designed for continuous background operation with menu-based access to all network features.*
