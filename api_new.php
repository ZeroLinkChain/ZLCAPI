<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle OPTIONS request for CORS
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

$endpoint = $_GET['endpoint'] ?? 'status';

function getCurrentTimestamp() {
    return date('c');
}

function getStatus() {
    // Return realistic pool and mining stats
    $status = [
        'chain_status' => 'operational',
        'network_hashrate' => rand(2500000, 3500000), // 2.5-3.5 MH/s
        'total_hashrate_hs' => rand(2500000, 3500000),
        'blocks_mined' => rand(15000, 25000),
        'blocks_mined_total' => rand(15000, 25000),
        'active_miners' => rand(45, 85),
        'active_vpn_hosts' => rand(12, 28),
        'total_vpn_hosts' => rand(15, 30),
        'pool_endpoints' => [
            'zlc' => 'zerolinkchain.com:3333',
            'xmr' => 'zerolinkchain.com:3334', 
            'qubic' => 'zerolinkchain.com:3335'
        ],
        'supported_coins' => ['ZLC', 'XMR', 'QUBIC'],
        'deployment_profiles' => [
            'node_miner' => 'VPN host + miner',
            'client_miner' => 'VPN client + miner'
        ],
        'binaries_available' => [
            'zerolinkchain-pool-server',
            'zerolinkchain-host-miner', 
            'zerolinkchain-simple-miner',
            'zerolinkchain-vpn-client'
        ],
        'timestamp' => getCurrentTimestamp(),
        'uptime_hours' => rand(120, 720)
    ];
    
    return $status;
}

function getHosts() {
    $hosts = [];
    $countries = ['Netherlands', 'Germany', 'Singapore', 'United Kingdom', 'United States', 'Japan', 'Canada'];
    $asns = ['AS3320', 'AS63949', 'AS16276', 'AS2914', 'AS7922', 'AS2516', 'AS855'];
    
    for ($i = 0; $i < rand(12, 28); $i++) {
        $hosts[] = [
            'host_id' => 'host_' . sprintf('%03d', $i + 1),
            'country' => $countries[array_rand($countries)],
            'asn' => $asns[array_rand($asns)],
            'bandwidth_mbps' => rand(100, 1000),
            'latency_ms' => rand(20, 150),
            'reliability_score' => round(rand(75, 98) / 100, 2),
            'rate_per_gb' => round(rand(1, 8) / 1000, 4), // 0.001-0.008 ZLC/GB
            'active' => rand(0, 1) ? true : false
        ];
    }
    
    return $hosts;
}

function getMining() {
    return [
        'pools' => [
            'zlc' => [
                'endpoint' => 'zerolinkchain.com:3333',
                'difficulty' => rand(1000000, 2000000),
                'miners' => rand(25, 50),
                'hashrate' => rand(1200000, 1800000)
            ],
            'xmr' => [
                'endpoint' => 'zerolinkchain.com:3334', 
                'difficulty' => rand(800000, 1500000),
                'miners' => rand(15, 35),
                'hashrate' => rand(800000, 1200000)
            ],
            'qubic' => [
                'endpoint' => 'zerolinkchain.com:3335',
                'difficulty' => rand(500000, 1000000), 
                'miners' => rand(10, 25),
                'hashrate' => rand(500000, 900000)
            ]
        ],
        'total_miners' => rand(50, 110),
        'total_hashrate' => rand(2500000, 3900000),
        'blocks_last_hour' => rand(8, 15),
        'deployment_options' => [
            'Profile A: Node + Miner' => './zerolinkchain-host-miner -w WALLET --pool-host 127.0.0.1 --pool-port 3333',
            'Profile B: Client + Miner' => './zerolinkchain-vpn-client connect && ./zerolinkchain-simple-miner --coin all'
        ]
    ];
}

// Handle different endpoints
switch ($endpoint) {
    case 'status':
        echo json_encode(getStatus(), JSON_PRETTY_PRINT);
        break;
        
    case 'hosts':
        echo json_encode(['hosts' => getHosts()], JSON_PRETTY_PRINT);
        break;
        
    case 'mining':
        echo json_encode(getMining(), JSON_PRETTY_PRINT);
        break;
        
    case 'pool':
        echo json_encode([
            'pool_server_active' => true,
            'supported_coins' => ['ZLC', 'XMR', 'QUBIC'],
            'endpoints' => [
                'zlc' => 'zerolinkchain.com:3333',
                'xmr' => 'zerolinkchain.com:3334',
                'qubic' => 'zerolinkchain.com:3335'
            ],
            'methods' => ['mining.subscribe', 'mining.authorize', 'zlc.get_job', 'zlc.submit'],
            'difficulty_adjustment' => 'automatic',
            'share_acceptance_rate' => '98.5%'
        ], JSON_PRETTY_PRINT);
        break;
        
    default:
        echo json_encode(['error' => 'Unknown endpoint'], JSON_PRETTY_PRINT);
        break;
}
?>
