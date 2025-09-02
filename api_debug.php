<?php
header('Content-Type: text/plain');

echo "=== ZeroLinkChain API Debug ===\n";
echo "Time: " . date('Y-m-d H:i:s') . "\n\n";

// Test 1: Basic connectivity
echo "1. Testing localhost:8001 connectivity...\n";
$socket = @fsockopen('localhost', 8001, $errno, $errstr, 1);
if ($socket) {
    echo "   ✅ Socket connection: SUCCESS\n";
    fclose($socket);
} else {
    echo "   ❌ Socket connection: FAILED ($errno: $errstr)\n";
}

// Test 2: Curl test
echo "\n2. Testing curl to localhost:8001/health...\n";
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, 'http://localhost:8001/health');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 2);
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 1);
$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

if ($response) {
    echo "   ✅ Curl response: SUCCESS\n";
    echo "   Response: $response\n";
} else {
    echo "   ❌ Curl response: FAILED\n";
    echo "   Error: $error\n";
    echo "   HTTP Code: $http_code\n";
}

// Test 3: file_get_contents test
echo "\n3. Testing file_get_contents...\n";
$context = stream_context_create([
    'http' => [
        'timeout' => 2,
        'ignore_errors' => true
    ]
]);
$result = @file_get_contents('http://localhost:8001/health', false, $context);
if ($result) {
    echo "   ✅ file_get_contents: SUCCESS\n";
    echo "   Response: $result\n";
} else {
    echo "   ❌ file_get_contents: FAILED\n";
}

echo "\n=== End Debug ===\n";
?>
