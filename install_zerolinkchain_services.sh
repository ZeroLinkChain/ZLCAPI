#!/bin/bash
# ZeroLinkChain Services Installation Script
# Installs wallet, mining pool, and node as systemd services

set -e

echo "🚀 ZeroLinkChain Services Installation"
echo "======================================"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root"
   exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p /var/lib/zerolinkchain/{wallet,pool,node}
mkdir -p /var/log/zerolinkchain
mkdir -p /etc/zerolinkchain

# Set permissions
chown -R root:root /var/lib/zerolinkchain
chmod -R 755 /var/lib/zerolinkchain
chmod 700 /var/lib/zerolinkchain/wallet  # Wallet data is sensitive

# Make Python scripts executable
echo "🔧 Setting up services..."
chmod +x services/wallet/zerolinkchain_wallet.py
chmod +x services/pool/zerolinkchain_pool.py
chmod +x services/node/zerolinkchain_node.py

# Install systemd service files
echo "⚙️  Installing systemd services..."
cp services/systemd/*.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install requests >/dev/null 2>&1 || {
    echo "⚠️  Warning: Could not install Python requests module"
    echo "   Please install manually: pip3 install requests"
}

# Create wallet first
echo "💰 Creating ZeroLinkChain wallet..."
cd services/wallet
python3 zerolinkchain_wallet.py create
WALLET_ADDRESS=$(python3 zerolinkchain_wallet.py info | grep -o 'ZLC[a-f0-9]\{61\}' | head -1)
echo "✅ Wallet created: $WALLET_ADDRESS"
cd ../..

# Enable and start services
echo "🔄 Starting services..."

# Start wallet service first
systemctl enable zerolinkchain-wallet.service
systemctl start zerolinkchain-wallet.service
sleep 2

# Start pool service (depends on wallet)
systemctl enable zerolinkchain-pool.service
systemctl start zerolinkchain-pool.service
sleep 2

# Start node service
systemctl enable zerolinkchain-node.service
systemctl start zerolinkchain-node.service
sleep 2

# Check service status
echo ""
echo "📊 Service Status:"
echo "=================="

services=("zerolinkchain-wallet" "zerolinkchain-pool" "zerolinkchain-node")
for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        echo "✅ $service: RUNNING"
    else
        echo "❌ $service: FAILED"
        echo "   Check logs: journalctl -u $service -f"
    fi
done

# Display service information
echo ""
echo "🔗 Service Information:"
echo "======================"
echo "Wallet Address: $WALLET_ADDRESS"
echo "Mining Pool Port: 8333"
echo "Node P2P Port: 8334"
echo "Node API Port: 8335"
echo ""
echo "📋 Management Commands:"
echo "======================"
echo "Check wallet balance:"
echo "  cd /var/www/html/services/wallet && python3 zerolinkchain_wallet.py balance"
echo ""
echo "Check pool stats:"
echo "  cd /var/www/html/services/pool && python3 zerolinkchain_pool.py stats"
echo ""
echo "Check node stats:"
echo "  cd /var/www/html/services/node && python3 zerolinkchain_node.py stats"
echo "  curl http://localhost:8335/stats"
echo ""
echo "View service logs:"
echo "  journalctl -u zerolinkchain-wallet -f"
echo "  journalctl -u zerolinkchain-pool -f"
echo "  journalctl -u zerolinkchain-node -f"
echo ""
echo "Restart services:"
echo "  systemctl restart zerolinkchain-wallet"
echo "  systemctl restart zerolinkchain-pool"
echo "  systemctl restart zerolinkchain-node"

# Create a simple miner for testing
echo ""
echo "⛏️  Creating test miner..."
cat > test_miner.py << 'EOF'
#!/usr/bin/env python3
"""
Simple ZeroLinkChain test miner
Connects to local pool and submits shares
"""

import socket
import json
import hashlib
import time
import random

def mine_share(work_template):
    """Mine a share for the given work template"""
    target = work_template['target']
    target_int = int(target, 16)
    
    # Simple mining loop
    for nonce in range(1000000):
        # Create block hash
        block_data = f"{work_template['previous_hash']}{work_template['coinbase_address']}{work_template['timestamp']}{nonce}"
        block_hash = hashlib.sha256(block_data.encode()).hexdigest()
        
        if int(block_hash, 16) <= target_int:
            return {
                'nonce': nonce,
                'hash': block_hash
            }
    
    return None

def main():
    print("🔗 ZeroLinkChain Test Miner")
    print("Connecting to local pool on port 8333...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8333))
        
        while True:
            # Receive work template
            data = sock.recv(4096).decode().strip()
            if data:
                work = json.loads(data)
                
                if work.get('type') == 'keepalive':
                    continue
                
                print(f"📋 Received work: height {work.get('height')}, difficulty {work.get('difficulty')}")
                
                # Mine a share
                share = mine_share(work)
                if share:
                    print(f"⛏️  Found share: {share['hash'][:16]}...")
                    
                    # Submit share
                    sock.send((json.dumps(share) + '\n').encode())
                    
                    # Get result
                    result_data = sock.recv(1024).decode().strip()
                    if result_data:
                        result = json.loads(result_data)
                        print(f"📊 Result: {result['result']}")
                        
                        if result['result'] == 'block_found':
                            print(f"🎉 BLOCK FOUND! Reward: {result['reward']} ZLC")
                        elif result['result'] == 'share_accepted':
                            print(f"✅ Share accepted! Reward: {result['reward']} ZLC")
                
                time.sleep(1)  # Small delay between shares
                
    except KeyboardInterrupt:
        print("\n⏹️  Miner stopped")
    except Exception as e:
        print(f"❌ Miner error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
EOF

chmod +x test_miner.py

echo "✅ Test miner created: ./test_miner.py"
echo ""
echo "🎯 Testing Instructions:"
echo "======================="
echo "1. Run the test miner: python3 test_miner.py"
echo "2. Check wallet balance after mining"
echo "3. Monitor service logs for activity"
echo ""
echo "🚀 ZeroLinkChain services are now running!"
echo "   All services will automatically restart on system reboot."
