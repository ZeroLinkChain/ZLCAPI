<?php
session_start();
header('Content-Type: application/json');

$is_dev_access = isset($_SESSION['dev_authenticated']) && $_SESSION['dev_authenticated'] === true;

if ($is_dev_access) {
    $data = [
        'status' => 'development',
        'real_data' => true,
        'system_load' => sys_getloadavg(),
        'timestamp' => date('c')
    ];
} else {
    $data = [
        'status' => 'launching_soon',
        'launch_date' => '2025-09-04T00:00:00Z'
    ];
}

echo json_encode($data);
?>
