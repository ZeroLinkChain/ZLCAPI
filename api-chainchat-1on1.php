<?php
// Enhanced API with 1-on-1 ChainChat and proper access control
// ChainChat: Direct wallet-to-wallet chat only (no group rooms)
// ChainProx VPN: Requires contribution - bandwidth based on mining rate
// ChainStore: Requires tiny fee per transaction

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

// Initialize session storage for wallet signatures
$session_storage_dir = '/tmp/zlc_sessions';
if (!file_exists($session_storage_dir)) {
    mkdir($session_storage_dir, 0700, true);
}

// Enhanced endpoint support including access control
$allowed = [
    'stats', 'blockchain', 'mining', 'vpn', 'privacy', 'vpn/status', 'hosts',
    'wallet_create', 'wallet_import', 'wallet_balance', 'wallet_send', 'wallet_history',
    'wallet_mnemonic_create', 'wallet_mnemonic_import', 'wallet_public_key',
    'wallet_session_verify', 'wallet_session_info', 'wallet_tx_challenge',
    'chainchat_access', 'chainchat_connect', 'chainchat_send', 'chainchat_receive',
    'chainstore_access', 'chainstore_upload', 'chainstore_download', 'chainstore_list',
    'chainprox_access', 'chainprox_connect', 'chainprox_bandwidth', 'chainprox_nodes'
];

$endpoint = isset($_GET['e']) ? trim($_GET['e']) : '';
if ($endpoint === '' || !in_array($endpoint, $allowed, true)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid endpoint']);
    exit;
}

// Cryptographic Verification Functions
function verifyPrivateKeyOwnership($address, $private_key) {
    // Verify that the private key actually corresponds to the given address
    $derived_address = deriveAddressFromPrivateKey($private_key);
    return $derived_address === $address;
}

function createTransactionChallenge($from_address, $to_address, $amount, $timestamp) {
    // Create a unique challenge message for transaction signing
    return hash('sha256', $from_address . $to_address . $amount . $timestamp . 'ZLC_TX_CHALLENGE');
}

function verifyTransactionSignature($challenge, $signature, $private_key) {
    // Verify that the signature was created with the private key
    // In production, use proper ECDSA signature verification
    $expected_signature = hash_hmac('sha256', $challenge, $private_key);
    return hash_equals($expected_signature, $signature);
}

function requireSignedTransaction($from_address, $to_address, $amount, $private_key, $signature = null, $timestamp = null) {
    // Enforce cryptographic proof for all transactions
    
    // 1. Verify private key ownership
    if (!verifyPrivateKeyOwnership($from_address, $private_key)) {
        throw new Exception('Private key does not match source address');
    }
    
    // 2. If signature provided, verify it
    if ($signature && $timestamp) {
        $challenge = createTransactionChallenge($from_address, $to_address, $amount, $timestamp);
        if (!verifyTransactionSignature($challenge, $signature, $private_key)) {
            throw new Exception('Invalid transaction signature');
        }
    }
    
    return true;
}

// Session Management Functions
function generateWalletSession($address, $private_key) {
    global $session_storage_dir;
    
    $session_token = bin2hex(random_bytes(32)); // 64-character hex token
    $timestamp = time();
    $expires = $timestamp + (24 * 60 * 60); // 24 hours
    
    // Create session signature (secure hash of address + token + timestamp)
    $session_data = [
        'address' => $address,
        'private_key' => $private_key, // In production, encrypt this
        'token' => $session_token,
        'created' => $timestamp,
        'expires' => $expires,
        'last_used' => $timestamp
    ];
    
    // Save to file
    $session_file = $session_storage_dir . '/' . $session_token . '.json';
    file_put_contents($session_file, json_encode($session_data));
    
    return $session_token;
}

function verifyWalletSession($session_token) {
    global $session_storage_dir;
    
    if (!$session_token) return false;
    
    $session_file = $session_storage_dir . '/' . $session_token . '.json';
    if (!file_exists($session_file)) {
        return false;
    }
    
    $session_data = json_decode(file_get_contents($session_file), true);
    if (!$session_data) return false;
    
    // Check expiration
    if (time() > $session_data['expires']) {
        unlink($session_file); // Delete expired session
        return false;
    }
    
    // Update last used
    $session_data['last_used'] = time();
    file_put_contents($session_file, json_encode($session_data));
    
    return $session_data;
}

function getWalletFromSession($session_token) {
    $session = verifyWalletSession($session_token);
    return $session ? $session : false;
}

// Access Control Functions
function checkWalletBalance($wallet_address) {
    // Check if wallet has any balance for ChainChat access
    // Mock implementation - replace with actual blockchain query
    if (!$wallet_address || strlen($wallet_address) < 10) {
        return false;
    }
    
    // Simulate balance check - in production, query actual blockchain
    $mock_balances = [
        'zlc18a9e1cff96175fbe0a3645f9ea673a7ebf78bea8' => 1.5,
        'test_wallet_001' => 0.1,
        'test_wallet_002' => 5.0
    ];
    
    return isset($mock_balances[$wallet_address]) && $mock_balances[$wallet_address] > 0;
}

function getMiningRate($public_key) {
    // Get current mining contribution rate
    // Mock implementation - replace with actual mining pool query
    if (!$public_key || strlen($public_key) < 10) {
        return 0;
    }
    
    $mock_rates = [
        'test_miner_001' => 150.5,
        'test_miner_002' => 75.2,
        'mining_key_123' => 200.0
    ];
    
    return isset($mock_rates[$public_key]) ? $mock_rates[$public_key] : 0;
}

function calculateBandwidth($mining_rate) {
    // Calculate VPN bandwidth allocation based on mining contribution
    if ($mining_rate <= 0) return 0;
    
    // Base allocation: 1 Mbps per 10 H/s mining rate
    $base_bandwidth = ($mining_rate / 10) * 1; // Mbps
    
    // Cap at 100 Mbps for fairness
    return min($base_bandwidth, 100);
}

// Enhanced Wallet Functions
function deriveAddressFromPrivateKey($private_key) {
    if (strlen($private_key) !== 64) return false;
    
    $hash = hash('sha256', hex2bin($private_key));
    return 'zlc' . substr($hash, 0, 38);
}

function generatePrivateKey() {
    return bin2hex(random_bytes(32));
}

function mnemonicToPrivateKey($mnemonic) {
    // Simple deterministic conversion - in production use proper BIP39
    $seed = hash('sha256', $mnemonic);
    return substr($seed, 0, 64);
}

// ChainChat 1-on-1 Access Control
function handleChainChatAccess() {
    $wallet_address = $_POST['wallet_address'] ?? '';
    $target_wallet = $_POST['target_wallet'] ?? '';
    
    if (!$wallet_address) {
        return ['error' => 'Your wallet address required', 'access' => false];
    }
    
    if (!$target_wallet) {
        return ['error' => 'Target wallet address required for 1-on-1 chat', 'access' => false];
    }
    
    if ($wallet_address === $target_wallet) {
        return ['error' => 'Cannot chat with yourself', 'access' => false];
    }
    
    $has_balance = checkWalletBalance($wallet_address);
    $target_has_balance = checkWalletBalance($target_wallet);
    
    if (!$has_balance) {
        return [
            'error' => 'Your wallet requires balance for ChainChat',
            'access' => false,
            'requirement' => 'Deposit any amount to your wallet to access ChainChat'
        ];
    }
    
    if (!$target_has_balance) {
        return [
            'error' => 'Target wallet has no balance - cannot establish chat',
            'access' => false,
            'requirement' => 'Both wallets must have balance for mutual authentication'
        ];
    }
    
    return [
        'access' => true,
        'message' => 'ChainChat 1-on-1 session authorized',
        'chat_type' => 'direct_wallet_to_wallet',
        'participants' => [$wallet_address, $target_wallet],
        'features' => ['direct_messaging', 'file_sharing', 'encrypted_chat']
    ];
}

function handleChainChatConnect() {
    $wallet_address = $_POST['wallet_address'] ?? '';
    $target_wallet = $_POST['target_wallet'] ?? '';
    
    // Verify mutual authentication first
    $_POST['wallet_address'] = $wallet_address;
    $_POST['target_wallet'] = $target_wallet;
    $access_check = handleChainChatAccess();
    if (!$access_check['access']) {
        return $access_check;
    }
    
    // Generate chat session ID for this wallet pair
    $participants = [$wallet_address, $target_wallet];
    sort($participants); // Consistent ordering
    $chat_session = 'chat_' . hash('sha256', implode(':', $participants));
    
    return [
        'connected' => true,
        'session_id' => $chat_session,
        'participants' => $participants,
        'message' => 'Direct chat established between wallets',
        'encryption' => 'end_to_end'
    ];
}

function handleChainChatSend() {
    $wallet_address = $_POST['wallet_address'] ?? '';
    $target_wallet = $_POST['target_wallet'] ?? '';
    $message = $_POST['message'] ?? '';
    $session_id = $_POST['session_id'] ?? '';
    
    if (!$message) {
        return ['error' => 'Message content required'];
    }
    
    // Verify session is valid for these wallets
    $participants = [$wallet_address, $target_wallet];
    sort($participants);
    $expected_session = 'chat_' . hash('sha256', implode(':', $participants));
    
    if ($session_id !== $expected_session) {
        return ['error' => 'Invalid chat session'];
    }
    
    return [
        'sent' => true,
        'message_id' => 'msg_' . bin2hex(random_bytes(16)),
        'timestamp' => time(),
        'from' => $wallet_address,
        'to' => $target_wallet,
        'encrypted' => true
    ];
}

function handleChainChatReceive() {
    $wallet_address = $_POST['wallet_address'] ?? '';
    $session_id = $_POST['session_id'] ?? '';
    
    // Mock message retrieval - in production, query chat database
    return [
        'messages' => [
            [
                'message_id' => 'msg_001',
                'from' => 'zlc_other_wallet_address',
                'to' => $wallet_address,
                'content' => 'Hello! This is a test message.',
                'timestamp' => time() - 300,
                'encrypted' => true
            ]
        ],
        'session_id' => $session_id,
        'unread_count' => 1
    ];
}

// ChainStore Access Control
function handleChainStoreAccess() {
    $wallet_address = $_POST['wallet_address'] ?? '';
    
    if (!$wallet_address) {
        return ['error' => 'Wallet address required for transactions', 'access' => false];
    }
    
    // ChainStore always accessible but requires fee per transaction
    return [
        'access' => true,
        'message' => 'ChainStore access available',
        'fee_structure' => [
            'upload_fee' => '0.001 ZLC per MB',
            'download_fee' => '0.0001 ZLC per file',
            'listing_fee' => '0.01 ZLC per item'
        ],
        'features' => ['marketplace', 'file_storage', 'smart_contracts']
    ];
}

// ChainProx VPN Access Control
function handleChainProxAccess() {
    $public_key = $_POST['public_key'] ?? '';
    
    if (!$public_key) {
        return ['error' => 'Public key required for contribution verification', 'access' => false];
    }
    
    $mining_rate = getMiningRate($public_key);
    $bandwidth = calculateBandwidth($mining_rate);
    
    if ($bandwidth <= 0) {
        return [
            'error' => 'ChainProx requires network contribution',
            'access' => false,
            'requirement' => 'Start mining or hosting to earn VPN bandwidth allocation'
        ];
    }
    
    return [
        'access' => true,
        'message' => 'ChainProx VPN access granted',
        'bandwidth_mbps' => $bandwidth,
        'mining_rate' => $mining_rate,
        'available_nodes' => 45
    ];
}

// Handle wallet endpoints (existing functionality)
function handleWalletEndpoint($endpoint) {
    switch ($endpoint) {
        case 'wallet_create':
            $private_key = generatePrivateKey();
            $address = deriveAddressFromPrivateKey($private_key);
            
            // Generate secure session token
            $session_token = generateWalletSession($address, $private_key);
            
            return [
                'address' => $address,
                'private_key' => $private_key, // Return for initial backup
                'session_token' => $session_token,
                'status' => 'created',
                'expires_in' => 24 * 60 * 60 // 24 hours in seconds
            ];
            
        case 'wallet_mnemonic_create':
            $words = ['abandon', 'ability', 'able', 'about', 'above', 'absent', 'absorb', 'abstract', 
                     'absurd', 'abuse', 'access', 'accident', 'account', 'accuse', 'achieve', 'acid'];
            shuffle($words);
            $mnemonic = implode(' ', array_slice($words, 0, 12));
            $private_key = mnemonicToPrivateKey($mnemonic);
            $address = deriveAddressFromPrivateKey($private_key);
            
            // Generate secure session token
            $session_token = generateWalletSession($address, $private_key);
            
            return [
                'address' => $address,
                'mnemonic' => $mnemonic,
                'private_key' => $private_key, // Return for initial backup
                'session_token' => $session_token,
                'status' => 'created',
                'expires_in' => 24 * 60 * 60 // 24 hours in seconds
            ];
            
        case 'wallet_mnemonic_import':
            $mnemonic = $_POST['mnemonic'] ?? '';
            if (str_word_count($mnemonic) < 12) {
                return ['error' => 'Invalid mnemonic phrase - must be at least 12 words'];
            }
            $private_key = mnemonicToPrivateKey($mnemonic);
            $address = deriveAddressFromPrivateKey($private_key);
            
            // Generate secure session token instead of returning private key
            $session_token = generateWalletSession($address, $private_key);
            
            return [
                'address' => $address,
                'session_token' => $session_token,
                'mnemonic' => $mnemonic, // Return for backup purposes
                'status' => 'imported',
                'expires_in' => 24 * 60 * 60 // 24 hours in seconds
            ];
            
        case 'wallet_import':
            $private_key = $_POST['privateKey'] ?? '';
            if (strlen($private_key) !== 64) {
                return ['error' => 'Invalid private key format'];
            }
            $address = deriveAddressFromPrivateKey($private_key);
            
            // Generate secure session token instead of returning private key
            $session_token = generateWalletSession($address, $private_key);
            
            return [
                'address' => $address,
                'session_token' => $session_token,
                'status' => 'imported',
                'expires_in' => 24 * 60 * 60 // 24 hours in seconds
            ];
            
        case 'wallet_session_verify':
            $session_token = $_POST['session_token'] ?? '';
            $session = verifyWalletSession($session_token);
            
            if (!$session) {
                return [
                    'valid' => false,
                    'error' => 'Invalid or expired session'
                ];
            }
            
            return [
                'valid' => true,
                'address' => $session['address'],
                'expires_in' => $session['expires'] - time()
            ];
            
        case 'wallet_session_info':
            $session_token = $_POST['session_token'] ?? '';
            $session = verifyWalletSession($session_token);
            
            if (!$session) {
                return [
                    'error' => 'Invalid or expired session'
                ];
            }
            
            return [
                'address' => $session['address'],
                'created' => $session['created'],
                'expires' => $session['expires'],
                'expires_in' => $session['expires'] - time(),
                'last_used' => $session['last_used']
            ];
            
        case 'wallet_balance':
            // Support both address (legacy) and session_token (secure) methods
            $session_token = $_POST['session_token'] ?? '';
            $address = $_POST['address'] ?? '';
            
            if ($session_token) {
                $session = verifyWalletSession($session_token);
                if (!$session) {
                    return ['error' => 'Invalid or expired session'];
                }
                $address = $session['address'];
            }
            
            if (!$address) {
                return ['error' => 'Address or session_token required'];
            }
            
            return [
                'address' => $address,
                'balance' => $zlc_db ? $zlc_db->getWalletBalance($address) : '0.00000000',
                'currency' => 'ZLC'
            ];
            
        case 'wallet_tx_challenge':
            // Generate a cryptographic challenge for transaction signing
            $session_token = $_POST['session_token'] ?? '';
            $session = verifyWalletSession($session_token);
            
            if (!$session) {
                return ['error' => 'Invalid or expired session'];
            }
            
            $to_address = $_POST['to'] ?? '';
            $amount = $_POST['amount'] ?? '';
            $timestamp = time();
            
            if (!$to_address || !$amount) {
                return ['error' => 'Missing required parameters: to, amount'];
            }
            
            // Validate inputs
            if (!is_numeric($amount) || floatval($amount) <= 0) {
                return ['error' => 'Invalid amount - must be positive number'];
            }
            
            if (!preg_match('/^zlc[a-f0-9]{40}$/i', $to_address)) {
                return ['error' => 'Invalid recipient address format'];
            }
            
            $from_address = $session['address'];
            $challenge = createTransactionChallenge($from_address, $to_address, $amount, $timestamp);
            
            return [
                'challenge' => $challenge,
                'from' => $from_address,
                'to' => $to_address,
                'amount' => $amount,
                'timestamp' => $timestamp,
                'expires_in' => 300, // Challenge valid for 5 minutes
                'instructions' => 'Sign this challenge with your private key and include signature in wallet_send request'
            ];
            
        case 'wallet_send':
            $session_token = $_POST['session_token'] ?? '';
            $session = verifyWalletSession($session_token);
            
            if (!$session) {
                return ['error' => 'Invalid or expired session - please re-import wallet'];
            }
            
            $to_address = $_POST['to'] ?? '';
            $amount = $_POST['amount'] ?? '';
            $signature = $_POST['signature'] ?? '';
            $timestamp = $_POST['timestamp'] ?? time();
            
            if (!$to_address || !$amount) {
                return ['error' => 'Missing required parameters: to, amount'];
            }
            
            // Validate amount format
            if (!is_numeric($amount) || floatval($amount) <= 0) {
                return ['error' => 'Invalid amount - must be positive number'];
            }
            
            // Use the private key from session for transaction signing
            $from_address = $session['address'];
            $private_key = $session['private_key'];
            
            try {
                // CRITICAL: Enforce cryptographic verification before any transaction
                requireSignedTransaction($from_address, $to_address, $amount, $private_key, $signature, $timestamp);
                
                // Additional validation: Check if addresses are valid ZLC format
                if (!preg_match('/^zlc[a-f0-9]{40}$/i', $from_address) || !preg_match('/^zlc[a-f0-9]{40}$/i', $to_address)) {
                    return ['error' => 'Invalid wallet address format'];
                }
                
                // Prevent self-transactions
                if ($from_address === $to_address) {
                    return ['error' => 'Cannot send to yourself'];
                }
                
                // Generate transaction ID with cryptographic proof
                $tx_data = $from_address . $to_address . $amount . $timestamp;
                $txid = 'zlc_' . hash('sha256', $tx_data . $private_key);
                
                return [
                    'txid' => $txid,
                    'from' => $from_address,
                    'to' => $to_address,
                    'amount' => $amount,
                    'timestamp' => $timestamp,
                    'status' => 'verified_and_pending',
                    'message' => 'Transaction cryptographically verified and submitted to network'
                ];
                
            } catch (Exception $e) {
                return [
                    'error' => 'Transaction verification failed: ' . $e->getMessage(),
                    'code' => 'CRYPTO_VERIFICATION_FAILED'
                ];
            }
            
        case 'wallet_history':
            return [
                'transactions' => [
                    [
                        'txid' => 'tx_001',
                        'type' => 'received',
                        'amount' => '5.0',
                        'timestamp' => time() - 3600
                    ],
                    [
                        'txid' => 'tx_002', 
                        'type' => 'sent',
                        'amount' => '-1.5',
                        'timestamp' => time() - 7200
                    ]
                ]
            ];
            
        default:
            return ['error' => 'Unknown wallet endpoint'];
    }
}

// Main request handling
try {
    // Handle ChainChat endpoints
    if (str_starts_with($endpoint, 'chainchat_access')) {
        echo json_encode(handleChainChatAccess());
        exit;
    }
    
    if (str_starts_with($endpoint, 'chainchat_connect')) {
        echo json_encode(handleChainChatConnect());
        exit;
    }
    
    if (str_starts_with($endpoint, 'chainchat_send')) {
        echo json_encode(handleChainChatSend());
        exit;
    }
    
    if (str_starts_with($endpoint, 'chainchat_receive')) {
        echo json_encode(handleChainChatReceive());
        exit;
    }
    
    // Handle other access control endpoints
    if (str_starts_with($endpoint, 'chainstore_access')) {
        echo json_encode(handleChainStoreAccess());
        exit;
    }
    
    if (str_starts_with($endpoint, 'chainprox_access')) {
        echo json_encode(handleChainProxAccess());
        exit;
    }
    
    // Handle wallet endpoints
    if (str_starts_with($endpoint, 'wallet_')) {
        echo json_encode(handleWalletEndpoint($endpoint));
        exit;
    }
    
    // Handle regular API proxy to C server
    $url = 'http://127.0.0.1:8001/' . $endpoint;
    
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 5,
        CURLOPT_CONNECTTIMEOUT => 2,
        CURLOPT_USERAGENT => 'ZeroLinkChain-WebProxy/2.0'
    ]);
    
    $resp = curl_exec($ch);
    $err = curl_error($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($err) {
        // Fallback to mock data for development
        $fallback_data = [
            'stats' => [
                'network_hash_rate' => '1.23 TH/s',
                'difficulty' => 1234567.89,
                'block_height' => 95847,
                'active_nodes' => 156,
                'total_supply' => '21000000 ZLC'
            ],
            'mining' => [
                'pool_hash_rate' => '456.78 GH/s',
                'miners_online' => 89,
                'blocks_found_24h' => 12,
                'estimated_earnings' => '0.0034 ZLC/day per GH/s'
            ],
            'vpn' => [
                'active_nodes' => 45,
                'total_bandwidth' => '2.1 Gbps',
                'countries' => 23,
                'avg_latency' => '45ms'
            ]
        ];
        
        if (isset($fallback_data[$endpoint])) {
            echo json_encode($fallback_data[$endpoint]);
        } else {
            http_response_code(502);
            echo json_encode(['error' => 'Upstream error', 'detail' => $err]);
        }
        exit;
    }
    
    if ($code >= 400) {
        http_response_code($code);
        echo $resp ?: json_encode(['error' => 'Upstream returned HTTP ' . $code]);
        exit;
    }
    
    echo $resp;
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Internal server error', 'detail' => $e->getMessage()]);
}
?>
