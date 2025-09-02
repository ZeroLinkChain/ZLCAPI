#!/bin/bash
echo "🧪 ZeroLinkChain Complete API Testing"
echo "===================================="
echo ""

echo "🔗 1. BLOCKCHAIN CORE APIs"
echo "========================="
echo "✅ /api/health:"
curl -s "https://zerolinkchain.com/api/health" | jq .
echo ""

echo "✅ /api/miner/stats:"
curl -s "https://zerolinkchain.com/api/miner/stats" | jq .
echo ""

echo "✅ /api/rewards/pending:"
curl -s "https://zerolinkchain.com/api/rewards/pending" | jq .
echo ""

echo "✅ /api/integrity/status:"
curl -s "https://zerolinkchain.com/api/integrity/status" | jq .
echo ""

echo "🔐 2. PRIVACY APIs"
echo "================="
echo "✅ /api.php?e=privacy:"
curl -s "https://zerolinkchain.com/api.php?e=privacy" | jq .
echo ""

echo "💰 3. WALLET APIs"
echo "================"
echo "✅ Create wallet session:"
WALLET_RESPONSE=$(curl -s -X POST "https://zerolinkchain.com/api/wallet/create")
echo "$WALLET_RESPONSE" | jq .
SESSION_TOKEN=$(echo "$WALLET_RESPONSE" | jq -r '.session_token // empty')
echo ""

if [ ! -z "$SESSION_TOKEN" ]; then
    echo "✅ Get wallet balance (with session):"
    curl -s -H "Authorization: Bearer $SESSION_TOKEN" "https://zerolinkchain.com/api/wallet/balance" | jq .
    echo ""
fi

echo "🌐 4. LOCAL NODE APIs"
echo "==================="
echo "✅ Node stats (localhost:8335):"
curl -s "http://localhost:8335/stats" | jq .
echo ""

echo "✅ Node peers:"
curl -s "http://localhost:8335/peers" | jq .
echo ""

echo "📊 5. SERVICE STATUS"
echo "==================="
echo "✅ Wallet service:"
systemctl is-active zerolinkchain-wallet && echo "RUNNING" || echo "STOPPED"

echo "✅ Pool service:"
systemctl is-active zerolinkchain-pool && echo "RUNNING" || echo "STOPPED"

echo "✅ Node service:"
systemctl is-active zerolinkchain-node && echo "RUNNING" || echo "STOPPED"
echo ""

echo "🎯 6. INTEGRATION TEST"
echo "===================="
echo "✅ Local wallet info:"
cd /var/www/html/services/wallet
python3 zerolinkchain_wallet.py info | jq .
echo ""

echo "✅ Pool stats:"
cd /var/www/html/services/pool
python3 zerolinkchain_pool.py stats | jq .
echo ""

echo "✅ Node stats:"
cd /var/www/html/services/node
python3 zerolinkchain_node.py stats | jq .
echo ""

echo "🎉 API Testing Complete!"
echo "======================="
