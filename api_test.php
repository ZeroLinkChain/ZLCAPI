<?php
$API_BASE_URL = "http://localhost:8003";
$health = @file_get_contents($API_BASE_URL . "/health");
echo "API Test: ";
if ($health) {
    echo "SUCCESS - " . $health;
} else {
    echo "FAILED - No response from " . $API_BASE_URL;
}
?>
