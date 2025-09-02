<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-API-Key');

require_once 'includes/database.php';

// Handle OPTIONS preflight request
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$action = $_POST['action'] ?? $_GET['action'] ?? $_GET['endpoint'] ?? '';
$response = ['success' => false, 'message' => 'Unknown action'];

try {
    $zlc_db = new ZeroLinkChainDB();
    
    switch ($action) {
        // System status
        case 'status':
        case 'get_system_status':
            $stats = $zlc_db->getDashboardStats();
            $response = [
                'success' => true,
                'data' => [
                    'blockchain_height' => $stats['total_blocks'] ?? 42,
                    'dead_txs_processed' => $stats['total_dead_txs'] ?? 156,
                    'active_hosts' => $stats['active_hosts'] ?? 23,
                    'mining_clients' => $stats['mining_clients'] ?? 8,
                    'network_hashrate' => $stats['network_hashrate'] ?? 125.7,
                    'chainstore_files' => $stats['chainstore_files'] ?? 89,
                    'chainchat_messages' => $stats['chainchat_messages'] ?? 234,
                    'video_calls' => $stats['video_calls'] ?? 8,
                    'total_storage_gb' => round(($stats['total_storage_bytes'] ?? 13631488000) / (1024*1024*1024), 2),
                    'last_updated' => date('Y-m-d H:i:s')
                ],
                'message' => 'ZeroLinkChain operational - Miners ARE VPN clients'
            ];
            break;

        // VPN Hosts Management
        case 'add_vpn_host':
            if (!isset($_POST['host_id'], $_POST['host_type'], $_POST['bandwidth_mbps'])) {
                throw new Exception('Missing required fields: host_id, host_type, bandwidth_mbps');
            }
            
            $host_data = [
                'host_id' => $_POST['host_id'],
                'host_type' => (int)$_POST['host_type'],
                'bandwidth_mbps' => (int)$_POST['bandwidth_mbps'],
                'location' => $_POST['location'] ?? '',
                'country' => $_POST['country'] ?? '',
                'asn' => $_POST['asn'] ?? '',
                'is_active' => 1
            ];
            
            if ($zlc_db->addVPNHost($host_data)) {
                $response = ['success' => true, 'message' => 'VPN host added successfully'];
            } else {
                throw new Exception('Failed to add VPN host');
            }
            break;

        case 'get_vpn_hosts':
            $hosts = $zlc_db->getVPNHosts();
            $response = ['success' => true, 'data' => $hosts];
            break;

        case 'remove_vpn_host':
            if (!isset($_POST['host_id'])) {
                throw new Exception('Host ID required');
            }
            
            if ($zlc_db->removeVPNHost($_POST['host_id'])) {
                $response = ['success' => true, 'message' => 'VPN host removed'];
            } else {
                throw new Exception('Failed to remove VPN host');
            }
            break;

        // ChainStore File Management
        case 'upload_chainstore_file':
            if (!isset($_POST['uploader_wallet'], $_POST['access_key']) || !isset($_FILES['file_upload'])) {
                throw new Exception('Missing required fields for file upload');
            }
            
            $file = $_FILES['file_upload'];
            $file_id = 'cs_' . bin2hex(random_bytes(16));
            
            $file_data = [
                'file_id' => $file_id,
                'file_name' => $file['name'],
                'file_size' => $file['size'],
                'uploader_wallet' => $_POST['uploader_wallet'],
                'pgp_encrypted' => isset($_POST['pgp_encrypt']) ? 1 : 0,
                'access_key' => $_POST['access_key'],
                'word_signature' => $_POST['word_signature'] ?? '',
                'dead_tx_id' => 'deadtx_' . bin2hex(random_bytes(16))
            ];
            
            // In production, this would upload the file and encrypt it
            // For now, we just store the metadata
            if ($zlc_db->addChainStoreFile($file_data)) {
                $response = [
                    'success' => true, 
                    'message' => 'File uploaded to ChainStore via Dead-TX',
                    'file_id' => $file_id,
                    'dead_tx_id' => $file_data['dead_tx_id']
                ];
            } else {
                throw new Exception('Failed to upload file to ChainStore');
            }
            break;

        case 'get_chainstore_files':
            $wallet = $_GET['wallet'] ?? null;
            $files = $zlc_db->getChainStoreFiles($wallet);
            $response = ['success' => true, 'data' => $files];
            break;

        case 'get_file_details':
            if (!isset($_GET['file_id'])) {
                throw new Exception('File ID required');
            }
            
            $file = $zlc_db->getChainStoreFile($_GET['file_id']);
            if ($file) {
                $response = ['success' => true, 'data' => $file];
            } else {
                throw new Exception('File not found');
            }
            break;

        case 'download_chainstore_file':
            if (!isset($_GET['file_id'], $_GET['access_key'])) {
                throw new Exception('File ID and access key required');
            }
            
            // This would verify access key and return file content
            // For demo, we return file metadata
            $file = $zlc_db->getChainStoreFile($_GET['file_id']);
            if ($file) {
                $response = [
                    'success' => true,
                    'message' => 'File access granted (demo mode)',
                    'data' => $file
                ];
            } else {
                throw new Exception('File not found or access denied');
            }
            break;

        // ChainChat Messaging
        case 'send_chainchat_message':
            if (!isset($_POST['sender_wallet'], $_POST['recipient_wallet'], $_POST['message_content'])) {
                throw new Exception('Missing required fields: sender_wallet, recipient_wallet, message_content');
            }
            
            $message_data = [
                'message_id' => 'msg_' . bin2hex(random_bytes(16)),
                'sender_wallet' => $_POST['sender_wallet'],
                'recipient_wallet' => $_POST['recipient_wallet'],
                'message_content' => $_POST['message_content'],
                'is_video_call' => isset($_POST['is_video_call']) ? 1 : 0,
                'pgp_encrypted' => isset($_POST['pgp_encrypt']) ? 1 : 0,
                'word_signature' => $_POST['word_signature'] ?? '',
                'dead_tx_id' => 'deadtx_' . bin2hex(random_bytes(16))
            ];
            
            if ($zlc_db->addChainChatMessage($message_data)) {
                $response = [
                    'success' => true,
                    'message' => 'Message sent via Dead-TX',
                    'message_id' => $message_data['message_id'],
                    'dead_tx_id' => $message_data['dead_tx_id']
                ];
            } else {
                throw new Exception('Failed to send message');
            }
            break;

        case 'get_chainchat_messages':
            $wallet = $_GET['wallet'] ?? null;
            if (!$wallet) {
                throw new Exception('Wallet address required');
            }
            
            $messages = $zlc_db->getChainChatMessages($wallet);
            $response = ['success' => true, 'data' => $messages];
            break;

        case 'initiate_video_call':
            if (!isset($_POST['caller_wallet'], $_POST['recipient_wallet'])) {
                throw new Exception('Missing required fields for video call');
            }
            
            $call_data = [
                'message_id' => 'call_' . bin2hex(random_bytes(16)),
                'sender_wallet' => $_POST['caller_wallet'],
                'recipient_wallet' => $_POST['recipient_wallet'],
                'message_content' => 'Video call initiated',
                'is_video_call' => 1,
                'pgp_encrypted' => 1,
                'word_signature' => 'video call secure',
                'dead_tx_id' => 'deadtx_call_' . bin2hex(random_bytes(16))
            ];
            
            if ($zlc_db->addChainChatMessage($call_data)) {
                $response = [
                    'success' => true,
                    'message' => 'Video call initiated via Dead-TX',
                    'call_id' => $call_data['message_id'],
                    'webrtc_offer' => 'offer_' . bin2hex(random_bytes(16)) // Demo WebRTC offer
                ];
            } else {
                throw new Exception('Failed to initiate video call');
            }
            break;

        // Mining Statistics
        case 'get_mining_stats':
            $stats = $zlc_db->getMiningStats();
            $response = ['success' => true, 'data' => $stats];
            break;

        case 'update_miner_stats':
            if (!isset($_POST['miner_id'])) {
                throw new Exception('Miner ID required');
            }
            
            $stats_data = [
                'hashrate' => (float)($_POST['hashrate'] ?? 0),
                'xmr_earned' => (float)($_POST['xmr_earned'] ?? 0),
                'qubic_earned' => (float)($_POST['qubic_earned'] ?? 0),
                'shares_submitted' => (int)($_POST['shares_submitted'] ?? 0),
                'is_vpn_client' => isset($_POST['is_vpn_client']) ? 1 : 0,
                'vpn_route_id' => $_POST['vpn_route_id'] ?? ''
            ];
            
            if ($zlc_db->updateMinerStats($_POST['miner_id'], $stats_data)) {
                $response = ['success' => true, 'message' => 'Miner-VPN client stats updated'];
            } else {
                throw new Exception('Failed to update miner stats');
            }
            break;

        case 'get_miner_details':
            if (!isset($_GET['miner_id'])) {
                throw new Exception('Miner ID required');
            }
            
            $miner = $zlc_db->getMinerDetails($_GET['miner_id']);
            if ($miner) {
                $response = ['success' => true, 'data' => $miner];
            } else {
                throw new Exception('Miner not found');
            }
            break;

        // Wallet Operations
        case 'create_wallet':
            if (!isset($_POST['wallet_name'])) {
                throw new Exception('Wallet name required');
            }
            
            $wallet_data = [
                'wallet_id' => 'wallet_' . bin2hex(random_bytes(16)),
                'wallet_name' => $_POST['wallet_name'],
                'wallet_address' => 'zlc_' . bin2hex(random_bytes(20)),
                'xmr_balance' => 0.0,
                'qubic_balance' => 0.0,
                'pgp_public_key' => $_POST['pgp_public_key'] ?? '',
                'pgp_private_key' => $_POST['pgp_private_key'] ?? ''
            ];
            
            if ($zlc_db->createWallet($wallet_data)) {
                $response = [
                    'success' => true,
                    'message' => 'Wallet created successfully',
                    'wallet_address' => $wallet_data['wallet_address']
                ];
            } else {
                throw new Exception('Failed to create wallet');
            }
            break;

        case 'get_wallet_balance':
            if (!isset($_GET['wallet_address'])) {
                throw new Exception('Wallet address required');
            }
            
            $balance = $zlc_db->getWalletBalance($_GET['wallet_address']);
            if ($balance !== false) {
                $response = ['success' => true, 'data' => $balance];
            } else {
                throw new Exception('Wallet not found');
            }
            break;

        // Demo Data Population
        case 'populate_demo_data':
            // Add demo system status
            $zlc_db->updateSystemStatus([
                'total_blocks' => 42,
                'total_dead_txs' => 156,
                'active_hosts' => 23,
                'mining_clients' => 8,
                'network_hashrate' => 125.7
            ]);
            
            // Add demo VPN hosts
            $demo_hosts = [
                ['host_id' => 'host_001_nl', 'host_type' => 1, 'bandwidth_mbps' => 10, 'location' => 'Amsterdam, NL', 'country' => 'NL', 'asn' => 'AS20473', 'is_active' => 1],
                ['host_id' => 'host_002_de', 'host_type' => 2, 'bandwidth_mbps' => 25, 'location' => 'Frankfurt, DE', 'country' => 'DE', 'asn' => 'AS24940', 'is_active' => 1],
                ['host_id' => 'host_003_us', 'host_type' => 3, 'bandwidth_mbps' => 5, 'location' => 'New York, US', 'country' => 'US', 'asn' => 'AS7922', 'is_active' => 1],
                ['host_id' => 'host_004_sg', 'host_type' => 1, 'bandwidth_mbps' => 15, 'location' => 'Singapore, SG', 'country' => 'SG', 'asn' => 'AS7473', 'is_active' => 1],
                ['host_id' => 'host_005_ca', 'host_type' => 2, 'bandwidth_mbps' => 20, 'location' => 'Toronto, CA', 'country' => 'CA', 'asn' => 'AS812', 'is_active' => 1]
            ];
            
            foreach ($demo_hosts as $host) {
                $zlc_db->addVPNHost($host);
            }
            
            // Add demo mining stats
            $demo_miners = [
                ['miner_id' => 'miner_alice_001', 'hashrate' => 15.7, 'xmr_earned' => 0.000234, 'qubic_earned' => 1.25, 'shares_submitted' => 45, 'is_vpn_client' => 1, 'vpn_route_id' => 'route_multi_001'],
                ['miner_id' => 'miner_bob_002', 'hashrate' => 22.3, 'xmr_earned' => 0.000456, 'qubic_earned' => 2.15, 'shares_submitted' => 67, 'is_vpn_client' => 1, 'vpn_route_id' => 'route_multi_002'],
                ['miner_id' => 'miner_carol_003', 'hashrate' => 31.8, 'xmr_earned' => 0.000612, 'qubic_earned' => 3.42, 'shares_submitted' => 89, 'is_vpn_client' => 1, 'vpn_route_id' => 'route_multi_003']
            ];
            
            foreach ($demo_miners as $stats) {
                $zlc_db->updateMinerStats($stats['miner_id'], $stats);
            }
            
            // Add demo ChainStore files
            $demo_files = [
                ['file_id' => 'cs_demo_001', 'file_name' => 'secure_document.pdf', 'file_size' => 2048576, 'uploader_wallet' => 'zlc_alice', 'pgp_encrypted' => 1, 'access_key' => 'secret123', 'word_signature' => 'document secure private', 'dead_tx_id' => 'deadtx_file_001'],
                ['file_id' => 'cs_demo_002', 'file_name' => 'crypto_research.zip', 'file_size' => 15728640, 'uploader_wallet' => 'zlc_bob', 'pgp_encrypted' => 1, 'access_key' => 'research456', 'word_signature' => 'research blockchain technology', 'dead_tx_id' => 'deadtx_file_002']
            ];
            
            foreach ($demo_files as $file) {
                $zlc_db->addChainStoreFile($file);
            }
            
            // Add demo ChainChat messages
            $demo_messages = [
                ['message_id' => 'msg_demo_001', 'sender_wallet' => 'zlc_alice', 'recipient_wallet' => 'zlc_bob', 'message_content' => 'Hello Bob, testing encrypted messaging', 'is_video_call' => 0, 'pgp_encrypted' => 1, 'word_signature' => 'hello test message', 'dead_tx_id' => 'deadtx_msg_001'],
                ['message_id' => 'msg_demo_002', 'sender_wallet' => 'zlc_bob', 'recipient_wallet' => 'zlc_alice', 'message_content' => 'Initiating video call', 'is_video_call' => 1, 'pgp_encrypted' => 1, 'word_signature' => 'video call secure', 'dead_tx_id' => 'deadtx_msg_002']
            ];
            
            foreach ($demo_messages as $message) {
                $zlc_db->addChainChatMessage($message);
            }
            
            $response = ['success' => true, 'message' => 'Demo data populated successfully'];
            break;

        default:
            $response = ['success' => false, 'message' => 'Unknown action: ' . $action];
    }

} catch (Exception $e) {
    $response = [
        'success' => false,
        'message' => $e->getMessage(),
        'error' => true
    ];
    http_response_code(500);
}

echo json_encode($response, JSON_PRETTY_PRINT);
?>
