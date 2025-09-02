<?php
// Simple same-origin proxy to the internal Flask API (port 8001)
// Prevents mixed-content and TLS issues by avoiding direct https requests to non-TLS port.

header('Content-Type: application/json; charset=utf-8');

// Allow only specific endpoints to mitigate SSRF risk
$allowed = [
    'stats',
    'blockchain',
    'mining',
    'vpn',
    'privacy',
    'vpn/status',
    'hosts'
];

$endpoint = isset($_GET['e']) ? trim($_GET['e']) : '';
if ($endpoint === '' || !in_array($endpoint, $allowed, true)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid endpoint']);
    exit;
}

$url = 'http://127.0.0.1:8001/' . $endpoint;

$ch = curl_init($url);
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 5,
    CURLOPT_CONNECTTIMEOUT => 2,
    CURLOPT_USERAGENT => 'ZeroLinkChain-WebProxy/1.0'
]);

$resp = curl_exec($ch);
$err  = curl_error($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($err) {
    http_response_code(502);
    echo json_encode(['error' => 'Upstream error', 'detail' => $err]);
    exit;
}

if ($code >= 400) {
    http_response_code($code);
    echo $resp ?: json_encode(['error' => 'Upstream returned HTTP ' . $code]);
    exit;
}

// Pass through upstream JSON
echo $resp;
?>