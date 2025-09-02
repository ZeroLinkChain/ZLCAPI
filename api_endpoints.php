<?php
// ZeroLinkChain API Endpoints - Direct proxy to C API servers
// Handles: /api/miner/stats, /api/rewards/pending, /api/integrity/status

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle CORS preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

// Parse the request path
$request_uri = $_SERVER['REQUEST_URI'];
$path = parse_url($request_uri, PHP_URL_PATH);

// Function to make HTTP request to C API server
function makeApiRequest($url) {
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 10,
        CURLOPT_CONNECTTIMEOUT => 5,
        CURLOPT_USERAGENT => 'ZeroLinkChain-WebProxy/1.0',
        CURLOPT_FOLLOWLOCATION => false,
        CURLOPT_SSL_VERIFYPEER => false
    ]);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $error = curl_error($ch);
    curl_close($ch);
    
    if ($error) {
        return [
            'success' => false,
            'error' => 'Connection failed: ' . $error,
            'url' => $url
        ];
    }
    
    if ($httpCode !== 200) {
        return [
            'success' => false,
            'error' => 'HTTP ' . $httpCode,
            'response' => $response,
            'url' => $url
        ];
    }
    
    return [
        'success' => true,
        'data' => $response
    ];
}

// Route API endpoints to the correct C API server
$api_servers = [8019, 8001]; // Try both servers
$endpoint_found = false;

foreach ($api_servers as $port) {
    if (strpos($path, '/api/miner/stats') !== false) {
        $url = "http://127.0.0.1:$port/api/miner/stats";
        $endpoint_found = true;
    } elseif (strpos($path, '/api/rewards/pending') !== false) {
        $url = "http://127.0.0.1:$port/api/rewards/pending";
        $endpoint_found = true;
    } elseif (strpos($path, '/api/integrity/status') !== false) {
        $url = "http://127.0.0.1:$port/api/integrity/status";
        $endpoint_found = true;
    } elseif (strpos($path, '/api/stats') !== false) {
        $url = "http://127.0.0.1:$port/api/stats";
        $endpoint_found = true;
    } elseif (strpos($path, '/api/health') !== false) {
        $url = "http://127.0.0.1:$port/api/health";
        $endpoint_found = true;
    }
    
    if ($endpoint_found) {
        $result = makeApiRequest($url);
        
        if ($result['success']) {
            // Success - return the data
            echo $result['data'];
            exit;
        } else {
            // Try next server
            continue;
        }
    }
}

// If no endpoint found or all servers failed
if (!$endpoint_found) {
    http_response_code(404);
    echo json_encode([
        'error' => 'Endpoint not found',
        'path' => $path,
        'available_endpoints' => [
            '/api/miner/stats',
            '/api/rewards/pending', 
            '/api/integrity/status',
            '/api/stats',
            '/api/health'
        ]
    ]);
} else {
    http_response_code(502);
    echo json_encode([
        'error' => 'All API servers unavailable',
        'servers_tried' => $api_servers,
        'endpoint' => $path
    ]);
}
?>
