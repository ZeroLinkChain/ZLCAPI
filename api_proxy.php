<?php
// ZeroLinkChain C API Proxy
// Routes API calls to the C backend servers

// Try multiple API servers in order of preference
$api_servers = [
    'http://127.0.0.1:8019',  // Full server with mining endpoints
    'http://127.0.0.1:8001'   // Basic API server
];

// Get the request path
$request_path = $_SERVER['REQUEST_URI'];
$method = $_SERVER['REQUEST_METHOD'];

// Handle CORS preflight
if ($method === 'OPTIONS') {
    header('Access-Control-Allow-Origin: *');
    header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type, Authorization');
    exit(0);
}

// Only proxy /api/ endpoints
if (strpos($request_path, '/api/') !== 0) {
    header('HTTP/1.1 404 Not Found');
    echo json_encode(['error' => 'not_found']);
    exit;
}

// Function to try API request on a server
function tryApiServer($server_url, $request_path, $method) {
    $url = $server_url . $request_path;

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 3);

    // Handle POST data
    if ($method === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        $post_data = file_get_contents('php://input');
        if ($post_data) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, $post_data);
        }

        // Forward Content-Type header
        $content_type = $_SERVER['CONTENT_TYPE'] ?? 'application/x-www-form-urlencoded';
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: ' . $content_type,
            'Content-Length: ' . strlen($post_data)
        ]);
    }

    // Execute request
    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $content_type = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
    $error = curl_error($ch);

    curl_close($ch);

    return [
        'success' => !$error && $http_code === 200,
        'response' => $response,
        'http_code' => $http_code,
        'content_type' => $content_type,
        'error' => $error,
        'url' => $url
    ];
}

// Try each API server until one works
$last_result = null;
foreach ($api_servers as $server_url) {
    $result = tryApiServer($server_url, $request_path, $method);

    if ($result['success']) {
        // Success! Forward the response
        http_response_code($result['http_code']);
        if ($result['content_type']) {
            header('Content-Type: ' . $result['content_type']);
        }

        // Add CORS headers
        header('Access-Control-Allow-Origin: *');
        header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
        header('Access-Control-Allow-Headers: Content-Type, Authorization');

        echo $result['response'];
        exit;
    }

    $last_result = $result;
}

// All servers failed
header('HTTP/1.1 502 Bad Gateway');
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

echo json_encode([
    'error' => 'all_backends_unavailable',
    'details' => $last_result ? $last_result['error'] : 'No servers available',
    'servers_tried' => $api_servers,
    'last_response' => $last_result ? $last_result['response'] : null
]);
?>
