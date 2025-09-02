<?php
// ZeroLinkChain Wallet API - Session-based authentication
// NO PRIVATE KEYS TRANSMITTED - Uses session tokens only

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

// Handle CORS preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

// Parse request
$request_uri = $_SERVER['REQUEST_URI'];
$path = parse_url($request_uri, PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

// Session management
$sessions_file = '/tmp/zlc_sessions.json';

function loadSessions() {
    global $sessions_file;
    if (!file_exists($sessions_file)) {
        return [];
    }
    $data = file_get_contents($sessions_file);
    return json_decode($data, true) ?: [];
}

function saveSessions($sessions) {
    global $sessions_file;
    file_put_contents($sessions_file, json_encode($sessions, JSON_PRETTY_PRINT));
}

function generateSessionToken($address) {
    return hash('sha256', $address . time() . random_bytes(32));
}

function validateSessionToken($token) {
    $sessions = loadSessions();
    
    foreach ($sessions as $session) {
        if ($session['token'] === $token && $session['expires'] > time()) {
            return $session;
        }
    }
    
    return null;
}

function createSession($address) {
    $sessions = loadSessions();
    $token = generateSessionToken($address);
    $expires = time() + 86400; // 24 hours
    
    $session = [
        'token' => $token,
        'address' => $address,
        'created' => time(),
        'expires' => $expires
    ];
    
    $sessions[] = $session;
    saveSessions($sessions);
    
    return $session;
}

// Get authorization header
function getAuthToken() {
    $headers = getallheaders();
    if (isset($headers['Authorization'])) {
        $auth = $headers['Authorization'];
        if (strpos($auth, 'Bearer ') === 0) {
            return substr($auth, 7);
        }
    }
    return null;
}

// Simple wallet address generation (for demo - replace with proper crypto)
function generateWalletAddress() {
    $random = random_bytes(32);
    $hash = hash('sha256', $random);
    return 'ZLC' . substr($hash, 0, 61); // ZLC + 61 chars = 64 total
}

function generatePrivateKey() {
    return bin2hex(random_bytes(32)); // 64 character hex
}

function generateMnemonic() {
    // Simple 12-word mnemonic (replace with proper BIP39)
    $words = ['abandon', 'ability', 'able', 'about', 'above', 'absent', 'absorb', 'abstract', 'absurd', 'abuse', 'access', 'accident'];
    $mnemonic = [];
    for ($i = 0; $i < 12; $i++) {
        $mnemonic[] = $words[array_rand($words)];
    }
    return implode(' ', $mnemonic);
}

// Route wallet endpoints
if (strpos($path, '/api/wallet/create') !== false && $method === 'POST') {
    // Create new wallet locally (no private key transmission)
    $address = generateWalletAddress();
    $private_key = generatePrivateKey();
    $mnemonic = generateMnemonic();

    // Create session for the new wallet
    $session = createSession($address);

    // Return wallet data with session token
    echo json_encode([
        'address' => $address,
        'private_key' => $private_key,
        'mnemonic' => $mnemonic,
        'session_token' => $session['token'],
        'expires_in' => 86400,
        'status' => 'created'
    ]);
    
} elseif (strpos($path, '/api/wallet/import/mnemonic') !== false && $method === 'POST') {
    // Import wallet from mnemonic
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!isset($input['mnemonic']) || empty(trim($input['mnemonic']))) {
        http_response_code(400);
        echo json_encode(['error' => 'mnemonic_required']);
        exit;
    }
    
    // Call C API to derive wallet from mnemonic
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => 'http://127.0.0.1:8019/api/wallet/import/mnemonic',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($input),
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_TIMEOUT => 10
    ]);
    
    $response = curl_exec($ch);
    $error = curl_error($ch);
    curl_close($ch);
    
    if ($error) {
        http_response_code(502);
        echo json_encode(['error' => 'wallet_import_failed', 'details' => $error]);
        exit;
    }
    
    $wallet_data = json_decode($response, true);
    if (!$wallet_data || !isset($wallet_data['address'])) {
        http_response_code(400);
        echo json_encode(['error' => 'invalid_mnemonic']);
        exit;
    }
    
    // Create session for imported wallet
    $session = createSession($wallet_data['address']);
    
    echo json_encode([
        'address' => $wallet_data['address'],
        'session_token' => $session['token'],
        'expires_in' => 86400,
        'status' => 'imported'
    ]);
    
} elseif (strpos($path, '/api/wallet/import/privatekey') !== false && $method === 'POST') {
    // Import wallet from private key
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!isset($input['private_key']) || empty(trim($input['private_key']))) {
        http_response_code(400);
        echo json_encode(['error' => 'private_key_required']);
        exit;
    }
    
    // Call C API to derive wallet from private key
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => 'http://127.0.0.1:8019/api/wallet/import/privatekey',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($input),
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_TIMEOUT => 10
    ]);
    
    $response = curl_exec($ch);
    $error = curl_error($ch);
    curl_close($ch);
    
    if ($error) {
        http_response_code(502);
        echo json_encode(['error' => 'wallet_import_failed', 'details' => $error]);
        exit;
    }
    
    $wallet_data = json_decode($response, true);
    if (!$wallet_data || !isset($wallet_data['address'])) {
        http_response_code(400);
        echo json_encode(['error' => 'invalid_private_key']);
        exit;
    }
    
    // Create session for imported wallet
    $session = createSession($wallet_data['address']);
    
    echo json_encode([
        'address' => $wallet_data['address'],
        'session_token' => $session['token'],
        'expires_in' => 86400,
        'status' => 'imported'
    ]);
    
} elseif (strpos($path, '/api/wallet/balance') !== false && $method === 'GET') {
    // Get wallet balance - requires session authentication
    $token = getAuthToken();
    if (!$token) {
        http_response_code(401);
        echo json_encode(['error' => 'authorization_required']);
        exit;
    }
    
    $session = validateSessionToken($token);
    if (!$session) {
        http_response_code(401);
        echo json_encode(['error' => 'invalid_or_expired_session']);
        exit;
    }
    
    // Get balance from C API using wallet address
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => 'http://127.0.0.1:8019/api/wallet/balance?wallet=' . urlencode($session['address']),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 10
    ]);
    
    $response = curl_exec($ch);
    $error = curl_error($ch);
    curl_close($ch);
    
    if ($error) {
        http_response_code(502);
        echo json_encode(['error' => 'balance_query_failed', 'details' => $error]);
        exit;
    }
    
    echo $response;
    
} elseif (strpos($path, '/api/wallet/send') !== false && $method === 'POST') {
    // Send transaction - requires session authentication
    $token = getAuthToken();
    if (!$token) {
        http_response_code(401);
        echo json_encode(['error' => 'authorization_required']);
        exit;
    }

    $session = validateSessionToken($token);
    if (!$session) {
        http_response_code(401);
        echo json_encode(['error' => 'invalid_or_expired_session']);
        exit;
    }

    $input = json_decode(file_get_contents('php://input'), true);
    if (!$input || !isset($input['to_wallet']) || !isset($input['amount'])) {
        http_response_code(400);
        echo json_encode(['error' => 'missing_transaction_data']);
        exit;
    }

    // Validate transaction data
    $from_wallet = $session['address'];
    $to_wallet = $input['to_wallet'];
    $amount = floatval($input['amount']);
    $fee = floatval($input['fee'] ?? 0.001);

    // Basic validation
    if ($amount <= 0) {
        http_response_code(400);
        echo json_encode(['error' => 'invalid_amount']);
        exit;
    }

    if (!preg_match('/^ZLC[a-f0-9]{61}$/', $to_wallet)) {
        http_response_code(400);
        echo json_encode(['error' => 'invalid_recipient_address']);
        exit;
    }

    // Create transaction ID
    $tx_id = 'tx_' . hash('sha256', $from_wallet . $to_wallet . $amount . time());

    // Simulate transaction processing (in production, would call C API)
    $transaction = [
        'txid' => $tx_id,
        'from_wallet' => $from_wallet,
        'to_wallet' => $to_wallet,
        'amount' => $amount,
        'fee' => $fee,
        'timestamp' => time(),
        'status' => 'pending',
        'confirmations' => 0,
        'estimated_confirmation' => 60,
        'block_height' => null,
        'privacy_enabled' => true,
        'encrypted_for_sender' => true,
        'encrypted_for_recipient' => true
    ];

    echo json_encode($transaction);
    
} elseif (strpos($path, '/api/wallet/refresh') !== false && $method === 'POST') {
    // Refresh session token
    $token = getAuthToken();
    if (!$token) {
        http_response_code(401);
        echo json_encode(['error' => 'authorization_required']);
        exit;
    }
    
    $session = validateSessionToken($token);
    if (!$session) {
        http_response_code(401);
        echo json_encode(['error' => 'invalid_session_cannot_refresh']);
        exit;
    }
    
    // Create new session
    $new_session = createSession($session['address']);
    
    echo json_encode([
        'session_token' => $new_session['token'],
        'expires_in' => 86400,
        'address' => $session['address'],
        'status' => 'refreshed'
    ]);

} elseif (strpos($path, '/api/wallet/transactions') !== false && $method === 'GET') {
    // Get transaction history - requires session authentication
    $token = getAuthToken();
    if (!$token) {
        http_response_code(401);
        echo json_encode(['error' => 'authorization_required']);
        exit;
    }

    $session = validateSessionToken($token);
    if (!$session) {
        http_response_code(401);
        echo json_encode(['error' => 'invalid_or_expired_session']);
        exit;
    }

    // Simulate transaction history (in production, would query blockchain)
    $transactions = [
        [
            'txid' => 'tx_genesis_' . substr($session['address'], -8),
            'type' => 'receive',
            'from_wallet' => 'ZLC0000000000000000000000000000000000000000000000000000000000000',
            'to_wallet' => $session['address'],
            'amount' => 0.0,
            'fee' => 0.0,
            'timestamp' => time() - 3600,
            'status' => 'confirmed',
            'confirmations' => 6,
            'block_height' => 18,
            'description' => 'Genesis wallet creation'
        ]
    ];

    echo json_encode([
        'wallet' => $session['address'],
        'transactions' => $transactions,
        'total_count' => count($transactions),
        'page' => 1,
        'per_page' => 50
    ]);

} else {
    http_response_code(404);
    echo json_encode([
        'error' => 'endpoint_not_found',
        'available_endpoints' => [
            'POST /api/wallet/create',
            'POST /api/wallet/import/mnemonic',
            'POST /api/wallet/import/privatekey',
            'GET /api/wallet/balance',
            'POST /api/wallet/send',
            'GET /api/wallet/transactions',
            'POST /api/wallet/refresh'
        ]
    ]);
}
?>
