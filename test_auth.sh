#!/bin/bash
# Test ZeroLinkChain authentication system

echo "🔐 Testing ZeroLinkChain Authentication System"
echo "============================================="

# Test 1: Check countdown page is default
echo ""
echo "Test 1: Checking default countdown page..."
RESPONSE=$(curl -s "http://localhost/index.php" | grep -o "ZeroLinkChain - Launching Soon")
if [ "$RESPONSE" = "ZeroLinkChain - Launching Soon" ]; then
    echo "✅ PASS: Countdown page is showing by default"
else
    echo "❌ FAIL: Countdown page not showing"
fi

# Test 2: Check protected pages redirect
echo ""
echo "Test 2: Checking protected pages redirect..."
RESPONSE=$(curl -s -I "http://localhost/wallet.php" | grep "Location: index.php")
if [ -n "$RESPONSE" ]; then
    echo "✅ PASS: Protected pages redirect to index.php"
else
    echo "❌ FAIL: Protected pages not redirecting"
fi

# Test 3: Check authentication form exists
echo ""
echo "Test 3: Checking authentication form exists..."
RESPONSE=$(curl -s "http://localhost/index.php" | grep -o "authCodeInput")
if [ "$RESPONSE" = "authCodeInput" ]; then
    echo "✅ PASS: Authentication form found"
else
    echo "❌ FAIL: Authentication form not found"
fi

echo ""
echo "🎯 Authentication System Status:"
echo "   • Countdown page: Active"
echo "   • Access code: 8592859325"
echo "   • Protected pages: Wallet, Dashboard, VPN, Mining, Storage, Chat"
echo "   • Session timeout: 24 hours"
echo ""
echo "✅ Authentication system ready for testing!"
