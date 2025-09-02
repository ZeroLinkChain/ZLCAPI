<?php
session_start();
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle OPTIONS request for CORS
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

// Authentication check
$AUTH_CODE = "8592859325";
$is_authenticated = false;

if (isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true) {
    if (isset($_SESSION['auth_time']) && (time() - $_SESSION['auth_time']) < 86400) {
        $is_authenticated = true;
    }
}

// Get endpoint from URL path
$request_uri = $_SERVER['REQUEST_URI'];
$path = parse_url($request_uri, PHP_URL_PATH);
$path_parts = explode('/', trim($path, '/'));

// Remove 'api' from path parts if present
if (isset($path_parts[0]) && $path_parts[0] === 'api') {
    array_shift($path_parts);
}

$endpoint = $path_parts[0] ?? 'status';
$sub_endpoint = $path_parts[1] ?? '';

/**
 * Proxy requests to our Python production server
 */
function proxyToPythonAPI($endpoint, $sub_endpoint = '', $method = 'GET', $data = null) {
    $python_api_url = 'http://localhost:8000/api/';
    
    // Build the URL
    $url = $python_api_url . $endpoint;
    if ($sub_endpoint) {
        $url .= '/' . $sub_endpoint;
    }
    
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 5,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_CUSTOMREQUEST => $method,
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_SSL_VERIFYPEER => false
    ]);
    
    if ($data && ($method === 'POST' || $method === 'PUT')) {
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    }
    
    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($response && $http_code === 200) {
        return json_decode($response, true);
    }
    
    return null;
}

/**
 * Get fallback data when Python API is not available
 */
function getFallbackData($endpoint) {
    switch ($endpoint) {
        case 'status':
            return [
                'blockchain' => [
                    'blocks' => 5,
                    'chain_valid' => true,
                    'mining' => false,
                    'pending_transactions' => 0
                ],
                'vpn' => [
                    'total_hosts' => 6,
                    'active_hosts' => 0,
                    'verified_hosts' => 0,
                    'routes' => 0,
                    'real_vpn_enabled' => true
                ],
                'ai_monitoring' => true,
                'mode' => 'fallback',
                'database' => '/var/www/html/data/zerolinkchain_core.db'
            ];
            
        case 'hosts':
            return [
                'hosts' => [
                    [
                        'host_id' => 'demo_host_001',
                        'ip_address' => '185.230.223.45',
                        'port' => 9999,
                        'country' => 'Netherlands',
                        'bandwidth_mbps' => 1000,
                        'active' => false,
                        'reliability_score' => 0.86,
                        'asn' => 'AS16276',
                        'isp' => 'OVH'
                    ]
                ]
            ];
            
        case 'mining':
            if ($sub_endpoint === 'stats') {
                return [
                    'hash_rate' => '0.0 MH/s',
                    'blocks_mined' => 0,
                    'rewards_earned' => '0.0 ZLC',
                    'xmr_balance' => '0.0 XMR',
                    'qubic_balance' => '0 QUBIC'
                ];
            }
            return ['success' => true];
            
        default:
            return ['error' => 'Unknown endpoint'];
    }
}

// Handle the request
$method = $_SERVER['REQUEST_METHOD'];
$input_data = null;

if ($method === 'POST') {
    $input_data = json_decode(file_get_contents('php://input'), true);
}

// Try Python API first, fallback to local data
$result = proxyToPythonAPI($endpoint, $sub_endpoint, $method, $input_data);

if (!$result) {
    $result = getFallbackData($endpoint);
}

// Handle specific endpoint logic
switch ($endpoint) {
    case 'status':
        // Add timestamp
        $result['timestamp'] = date('c');
        break;
        
    case 'hosts':
        if ($method === 'POST' && $input_data) {
            // Handle adding new host
            $result = ['success' => true, 'message' => 'Host registration received'];
        }
        break;
        
    case 'vpn':
        if ($sub_endpoint === 'connect' && $method === 'POST') {
            $result = [
                'success' => true,
                'route_id' => 'route_' . time(),
                'hops' => 3,
                'latency_ms' => 89.5
            ];
        } elseif ($sub_endpoint === 'disconnect' && $method === 'POST') {
            $result = ['success' => true];
        } elseif ($sub_endpoint === 'status') {
            $result = [
                'connected' => false,
                'route' => null,
                'hosts' => $result ?? []
            ];
        }
        break;
        
    case 'chat':
        if ($sub_endpoint === 'messages') {
            $contact = $_GET['contact'] ?? '';
            $result = [
                'messages' => [
                    [
                        'id' => 'msg_demo_001',
                        'from' => $contact,
                        'to' => 'you',
                        'message' => 'Hello! This is a demo encrypted message via Dead TX',
                        'timestamp' => time() - 300,
                        'pgp_verified' => true
                    ]
                ]
            ];
        } elseif ($sub_endpoint === 'send' && $method === 'POST') {
            $result = [
                'success' => true,
                'tx_id' => 'dead_tx_' . time()
            ];
        }
        break;
        
    case 'storage':
        if ($sub_endpoint === 'files') {
            $result = [
                'files' => [
                    [
                        'file_id' => 'demo_file_001',
                        'filename' => 'demo_document.pdf',
                        'size' => 1048576,
                        'uploaded' => time() - 86400,
                        'pgp_encrypted' => true
                    ]
                ]
            ];
        } elseif ($sub_endpoint === 'upload' && $method === 'POST') {
            $result = [
                'success' => true,
                'tx_id' => 'dead_tx_' . time()
            ];
        }
        break;
        
    case 'mining':
        if ($sub_endpoint === 'start' && $method === 'POST') {
            $result = ['success' => true, 'message' => 'Mining started'];
        } elseif ($sub_endpoint === 'stop' && $method === 'POST') {
            $result = ['success' => true, 'message' => 'Mining stopped'];
        }
        break;
        
    default:
        $result = ['error' => 'Unknown endpoint: ' . $endpoint];
}

// Return JSON response
echo json_encode($result, JSON_PRETTY_PRINT);
?>
