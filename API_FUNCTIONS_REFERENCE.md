# ZeroLinkChain API Functions Reference
## Complete Function Implementation Guide

### Core C API Functions

#### 1. HTTP Server Functions (`http_server.c`)

```c
// Main HTTP request handler
void handle_request(int client_socket, sqlite3 *db);

// Send HTTP response with proper headers
static void send_response(int client_socket, const char *status, const char *body);

// Parse query parameters from URL
static char* get_query_param(const char* query_string, const char* param_name);

// Handle GET requests
static void handle_get(int client_socket, const char *path, sqlite3 *db);

// Handle POST requests  
static void handle_post(int client_socket, const char *path, const char* body, sqlite3 *db);

// Start HTTP server on specified port
int zl_http_start(int port, sqlite3 *db);
```

#### 2. Mining Pool Functions (`mining.c`)

```c
// Initialize mining system and database tables
int zl_mining_init(sqlite3 *db);

// Get new mining work for a wallet
cJSON* zl_mining_get_work(sqlite3 *db, const char* wallet_address);

// Submit completed mining work
cJSON* zl_mining_submit_work(sqlite3 *db, const char* wallet_address, 
                           const char* work_id, long nonce, const char* hash);

// Get mining statistics for a wallet
cJSON* zl_mining_get_stats(sqlite3 *db, const char* wallet_address);

// Record hash rate for a wallet
int zl_mining_record_hashes(sqlite3 *db, const char* wallet_address, long hashes);

// Mine a block and update blockchain
int zl_mining_mine_block(sqlite3 *db, const char* wallet_address, const char* hash);

// Verify proof-of-work hash
static int verify_hash(const char* work_id, const char* target, long nonce, const char* submitted_hash);
```

#### 3. Proxy Pool Functions (`proxy_pool.c`)

```c
// Initialize proxy pool system
int zl_proxy_pool_init(sqlite3 *db);

// Register a new proxy node
int zl_proxy_pool_register_node(sqlite3 *db, const char* wallet_address, 
                               const char* ip_address, int port);

// Send heartbeat to maintain node status
int zl_proxy_pool_heartbeat(sqlite3 *db, const char* wallet_address);

// Record a proxy hop for billing
int zl_proxy_pool_record_hop(sqlite3 *db, const char* provider_wallet, 
                            const char* user_wallet);

// Get available proxy nodes
cJSON* zl_proxy_pool_get_nodes(sqlite3 *db, int limit);

// Scan subnet for proxy servers
cJSON* zl_proxy_pool_scan_subnet(sqlite3 *db, const char* subnet, 
                                int start_ip, int end_ip);

// Validate and test proxy servers
int zl_proxy_pool_scan_and_validate(sqlite3 *db);
```

#### 4. Wallet Functions (`wallet.c`)

```c
// Initialize wallet system
int zl_wallet_init(sqlite3 *db);

// Create new wallet if it doesn't exist
int zl_wallet_create(sqlite3 *db, const char* address);

// Get wallet information
int zl_wallet_get(sqlite3 *db, const char* address, wallet_t *wallet);

// Add mining reward to wallet
int zl_wallet_add_mining_reward(sqlite3 *db, const char* address, double amount);

// Add proxy fees to wallet
int zl_wallet_add_proxy_fee(sqlite3 *db, const char* address, double amount);

// Transfer funds between wallets
int zl_wallet_transfer(sqlite3 *db, const char* from_address, 
                      const char* to_address, double amount);

// Update wallet activity timestamp
int zl_wallet_update_activity(sqlite3 *db, const char* address);

// Record hash rate for wallet
int zl_wallet_record_hash(sqlite3 *db, const char* address, long hashes);
```

#### 5. Statistics Functions (`stats.c`)

```c
// Build comprehensive system statistics
cJSON *zl_build_stats(sqlite3 *db);

// Build proxy network statistics
cJSON *zl_build_proxy_stats(sqlite3 *db);

// Get mining statistics (internal)
static void get_mining_stats(sqlite3 *db, int *active_miners, 
                           double *hash_rate, int *blocks_found);

// Get VPN/proxy statistics (internal)
static void get_vpn_stats(sqlite3 *db, int *connected_hosts, int *total_bandwidth);
```

#### 6. Database Functions (`db.c`)

```c
// Open database connection
int zl_db_open(const char* db_path, sqlite3 **db);

// Close database connection
void zl_db_close(sqlite3 *db);

// Get current blockchain height
int zl_db_get_block_height(sqlite3 *db, long *height);

// Execute SQL with error handling
int zl_db_exec(sqlite3 *db, const char* sql);

// Prepare and execute parameterized queries
int zl_db_prepare_and_step(sqlite3 *db, const char* sql, ...);
```

#### 7. Transaction Logging Functions (`transaction_log.c`)

```c
// Initialize transaction logging system
int zl_transaction_init(sqlite3 *db);

// Log a transaction
int zl_transaction_log(sqlite3 *db, const char* wallet_address, 
                      int transaction_type, double amount, const char* details);

// Get transaction history for wallet
char* zl_transaction_history(sqlite3 *db, const char* wallet_address, int limit);

// Transaction types
typedef enum {
    TX_TYPE_TRANSFER = 1,
    TX_TYPE_MINING_REWARD = 2,
    TX_TYPE_PROXY_FEE = 3,
    TX_TYPE_SERVICE_FEE = 4
} transaction_type_t;
```

### Core Node Functions (`zerolinkchain_core.c`)

#### 1. VPN/Proxy Functions

```c
// Register a VPN host in the network
int register_vpn_host(vpn_host_t *host);

// Find optimal route through proxy network
vpn_route_t *find_optimal_route(const char *target_country, uint32_t min_bandwidth);

// Establish VPN connection through multiple hops
int establish_vpn_connection(vpn_route_t *route, int client_socket);

// Test if host is a working proxy server
int test_proxy_server(const char *ip, uint16_t port, const char *proxy_type);

// Scan for real proxy servers
void scan_for_real_proxies(void);

// Test host connectivity quickly
int test_host_fast(const char *ip, uint16_t port, float *response_time);

// Filter hosts based on criteria
int auto_filter_host(const char *ip, uint16_t port, const char *protocol);
```

#### 2. Mining Functions

```c
// Mining worker thread
void *mining_worker(void *arg);

// Mine a single block
int mine_block(block_t *block, uint32_t difficulty);

// Validate block hash
int validate_block_hash(const block_t *block);

// Add block to blockchain
int add_block_to_chain(const block_t *block);

// Calculate mining difficulty
uint32_t calculate_difficulty(void);
### CloudProx (Planned HTTP Exposure)
Core CloudProx functionality executes natively; forthcoming REST layer (draft):

| Function | Method | Path | Description |
| -------- | ------ | ---- | ----------- |
| Request Route | POST | /v1/cloudprox/route | Build multi-hop route (min_hops, min_bandwidth, required_protocol_flags) |
| List Hosts | GET | /v1/cloudprox/hosts | Sanitized host list (flags, region, reliability) |
| Route Status | GET | /v1/cloudprox/route/{id} | AEAD seq counters, hop meta (anonymized) |
| Metrics | GET | /v1/cloudprox/metrics | Aggregate bandwidth/diversity/reliability |

`required_protocol_flags`: bitmask AND of required capabilities. See `API_DOCUMENTATION.md` for flag table.

```

#### 3. Network Functions

```c
// VPN server worker thread
void *vpn_server_worker(void *arg);

// API server worker thread  
void *api_server_worker(void *arg);

// Auto-scanner worker thread
void *auto_scanner_worker(void *arg);

// AI monitor worker thread
void *ai_monitor_worker(void *arg);

// Handle VPN client connection
void handle_vpn_client(int client_socket);

// Process API request
void process_api_request(int client_socket, const char *request);
```

#### 4. Security Functions

```c
// Analyze host security
void analyze_host_security(const char *host_id);

// Detect suspicious patterns
void detect_suspicious_patterns(void);

// Validate transaction
int validate_transaction(const transaction_t *tx);

// Encrypt data for transmission
int encrypt_data(const uint8_t *input, size_t input_len, 
                uint8_t *output, size_t *output_len);

// Decrypt received data
int decrypt_data(const uint8_t *input, size_t input_len,
                uint8_t *output, size_t *output_len);
```

### Data Structures

#### 1. Core Structures

```c
// VPN Host structure
typedef struct {
    char host_id[64];
    char ip_address[16];
    uint16_t port;
    uint32_t bandwidth_mbps;
    uint32_t latency_ms;
    float reliability_score;
    char country[3];
    char asn[16];
    char isp[64];
    time_t last_seen;
    int is_active;
} vpn_host_t;

// VPN Route structure
typedef struct {
    char route_id[64];
    vpn_host_t *hosts[5];
    size_t hop_count;
    uint32_t total_latency;
    uint32_t min_bandwidth;
    int asn_diversity;
    int is_active;
} vpn_route_t;

// Wallet structure
typedef struct {
    char address[128];
    double balance;
    double mining_rewards;
    double proxy_fees;
    double service_fees;
    int blocks_mined;
    int proxy_hops_provided;
    time_t created_at;
    time_t last_activity;
    int active;
} wallet_t;

// Block structure
typedef struct {
    uint32_t height;
    char hash[65];
    char previous_hash[65];
    time_t timestamp;
    uint32_t difficulty;
    uint32_t nonce;
    char miner[128];
    uint64_t reward;
    uint32_t transaction_count;
    size_t block_size;
} block_t;
```

#### 2. Configuration Structure

```c
// Global configuration
typedef struct {
    uint32_t mining_interval_sec;
    uint32_t mining_threads;
    uint32_t difficulty;
    uint16_t vpn_port;
    uint16_t api_port;
    char data_dir[256];
    int log_level;
} zlc_config_t;
```

### API Endpoint Mapping

#### 1. GET Endpoints

```c
// Health check
if(strcmp(clean_path,"/health")==0) {
    send_response(c,"200 OK","{\"status\":\"ok\",\"service\":\"zerolinkchain_api\"}");
}

// System statistics
else if(strcmp(clean_path,"/stats")==0) {
    cJSON *root = zl_build_stats(db); 
    char *out = cJSON_PrintUnformatted(root); 
    cJSON_Delete(root);
    send_response(c,"200 OK",out); 
    free(out);
}

// Proxy statistics
else if(strcmp(clean_path,"/proxy/stats")==0) {
    cJSON *root = zl_build_proxy_stats(db); 
    char *out = cJSON_PrintUnformatted(root); 
    cJSON_Delete(root);
    send_response(c,"200 OK",out); 
    free(out);
}

// Proxy discovery
else if(strcmp(clean_path,"/api/proxy/discover")==0) {
    int limit = 10;  // Default limit
    if (query_string) {
        char *limit_str = get_query_param(query_string, "limit");
        if (limit_str) {
            limit = atoi(limit_str);
            if (limit <= 0 || limit > 100) limit = 10;
            free(limit_str);
        }
    }
    cJSON *root = zl_proxy_pool_get_nodes(db, limit);
    if (root) {
        char *out = cJSON_PrintUnformatted(root);
        cJSON_Delete(root);
        send_response(c, "200 OK", out);
        free(out);
    }
}

// Mining work request
else if(strcmp(clean_path,"/api/mining/work")==0) {
    if (!query_string) {
        send_response(c, "400 Bad Request", "{\"error\":\"wallet_required\"}");
        return;
    }
    char *wallet = get_query_param(query_string, "wallet");
    if (!wallet) {
        send_response(c, "400 Bad Request", "{\"error\":\"wallet_required\"}");
        return;
    }
    cJSON *work = zl_mining_get_work(db, wallet);
    if (work) {
        char *out = cJSON_PrintUnformatted(work);
        cJSON_Delete(work);
        send_response(c, "200 OK", out);
        free(out);
    }
    free(wallet);
}

// Mining statistics
else if(strcmp(clean_path,"/api/mining/stats")==0) {
    if (!query_string) {
        send_response(c, "400 Bad Request", "{\"error\":\"wallet_required\"}");
        return;
    }
    char *wallet = get_query_param(query_string, "wallet");
    if (!wallet) {
        send_response(c, "400 Bad Request", "{\"error\":\"wallet_required\"}");
        return;
    }
    cJSON *stats = zl_mining_get_stats(db, wallet);
    if (stats) {
        char *out = cJSON_PrintUnformatted(stats);
        cJSON_Delete(stats);
        send_response(c, "200 OK", out);
        free(out);
    }
    free(wallet);
}

// Wallet balance
else if(strcmp(clean_path,"/api/wallet/balance")==0) {
    if (!query_string) {
        send_response(c, "400 Bad Request", "{\"error\":\"wallet_required\"}");
        return;
    }
    char *wallet_addr = get_query_param(query_string, "wallet");
    if (!wallet_addr) {
        send_response(c, "400 Bad Request", "{\"error\":\"wallet_required\"}");
        return;
    }
    wallet_t wallet;
    if (zl_wallet_get(db, wallet_addr, &wallet) == 0) {
        cJSON *response = cJSON_CreateObject();
        cJSON_AddStringToObject(response, "wallet", wallet.address);
        cJSON_AddNumberToObject(response, "balance", wallet.balance);
        cJSON_AddNumberToObject(response, "mining_rewards", wallet.mining_rewards);
        cJSON_AddNumberToObject(response, "proxy_fees", wallet.proxy_fees);
        cJSON_AddNumberToObject(response, "service_fees", wallet.service_fees);
        cJSON_AddNumberToObject(response, "blocks_mined", wallet.blocks_mined);
        cJSON_AddNumberToObject(response, "proxy_hops", wallet.proxy_hops_provided);
        cJSON_AddBoolToObject(response, "active", wallet.active);
        
        char *out = cJSON_PrintUnformatted(response);
        cJSON_Delete(response);
        send_response(c, "200 OK", out);
        free(out);
    } else {
        send_response(c, "404 Not Found", "{\"error\":\"wallet_not_found\"}");
    }
    free(wallet_addr);
}

// Transaction history
else if(strcmp(clean_path,"/api/wallet/history")==0) {
    if (!query_string) {
        send_response(c, "400 Bad Request", "{\"error\":\"wallet_required\"}");
        return;
    }
    char *wallet_addr = get_query_param(query_string, "wallet");
    if (!wallet_addr) {
        send_response(c, "400 Bad Request", "{\"error\":\"wallet_required\"}");
        return;
    }
    char *limit_str = get_query_param(query_string, "limit");
    int limit = limit_str ? atoi(limit_str) : 10;
    if (limit <= 0 || limit > 100) limit = 10;
    if (limit_str) free(limit_str);

    char *history = zl_transaction_history(db, wallet_addr, limit);
    if (history) {
        send_response(c, "200 OK", history);
        free(history);
    } else {
        send_response(c, "500 Internal Server Error", "{\"error\":\"failed_to_get_history\"}");
    }
    free(wallet_addr);
}
```

#### 2. POST Endpoints

```c
// Proxy node registration
if (strcmp(path, "/api/proxy/register") == 0) {
    if (!json) {
        send_response(c, "400 Bad Request", "{\"error\":\"invalid_json\"}");
        return;
    }
    cJSON *wallet = cJSON_GetObjectItem(json, "wallet");
    cJSON *ip = cJSON_GetObjectItem(json, "ip");
    cJSON *port = cJSON_GetObjectItem(json, "port");
    
    if (!wallet || !ip || !port) {
        send_response(c, "400 Bad Request", "{\"error\":\"missing_fields\"}");
        cJSON_Delete(json);
        return;
    }
    
    int result = zl_proxy_pool_register_node(db, 
        cJSON_GetStringValue(wallet),
        cJSON_GetStringValue(ip),
        cJSON_GetNumberValue(port));
    
    if (result == 0) {
        response = cJSON_CreateObject();
        cJSON_AddStringToObject(response, "status", "registered");
        cJSON_AddStringToObject(response, "wallet", cJSON_GetStringValue(wallet));
    } else {
        response = cJSON_CreateObject();
        cJSON_AddStringToObject(response, "error", "registration_failed");
    }
}

// Proxy heartbeat
else if (strcmp(path, "/api/proxy/heartbeat") == 0) {
    if (!json) {
        send_response(c, "400 Bad Request", "{\"error\":\"invalid_json\"}");
        return;
    }
    cJSON *wallet = cJSON_GetObjectItem(json, "wallet");
    if (!wallet) {
        send_response(c, "400 Bad Request", "{\"error\":\"missing_wallet\"}");
        cJSON_Delete(json);
        return;
    }
    
    int result = zl_proxy_pool_heartbeat(db, cJSON_GetStringValue(wallet));
    
    if (result == 0) {
        response = cJSON_CreateObject();
        cJSON_AddStringToObject(response, "status", "ok");
    } else {
        response = cJSON_CreateObject();
        cJSON_AddStringToObject(response, "error", "heartbeat_failed");
    }
}

// Record proxy hop
else if (strcmp(path, "/api/proxy/hop") == 0) {
    if (!json) {
        send_response(c, "400 Bad Request", "{\"error\":\"invalid_json\"}");
        return;
    }
    cJSON *provider = cJSON_GetObjectItem(json, "provider_wallet");
    cJSON *user = cJSON_GetObjectItem(json, "user_wallet");
    
    if (!provider) {
        send_response(c, "400 Bad Request", "{\"error\":\"missing_provider_wallet\"}");
        cJSON_Delete(json);
        return;
    }
    
    int result = zl_proxy_pool_record_hop(db, 
        cJSON_GetStringValue(provider),
        user ? cJSON_GetStringValue(user) : "");
    
    if (result == 0) {
        response = cJSON_CreateObject();
        cJSON_AddStringToObject(response, "status", "recorded");
        cJSON_AddNumberToObject(response, "fee", 0.001);
    } else {
        response = cJSON_CreateObject();
        cJSON_AddStringToObject(response, "error", "recording_failed");
    }
}

// Mining work submission
else if (strcmp(path, "/api/mining/submit") == 0) {
    if (!json) {
        send_response(c, "400 Bad Request", "{\"error\":\"invalid_json\"}");
        return;
    }
    cJSON *wallet = cJSON_GetObjectItem(json, "wallet");
    cJSON *work_id = cJSON_GetObjectItem(json, "work_id");
    cJSON *nonce = cJSON_GetObjectItem(json, "nonce");
    cJSON *hash = cJSON_GetObjectItem(json, "hash");
    
    if (!wallet || !work_id || !nonce || !hash) {
        send_response(c, "400 Bad Request", "{\"error\":\"missing_fields\"}");
        cJSON_Delete(json);
        return;
    }
    
    response = zl_mining_submit_work(db,
        cJSON_GetStringValue(wallet),
        cJSON_GetStringValue(work_id),
        (long)cJSON_GetNumberValue(nonce),
        cJSON_GetStringValue(hash));
}

// Wallet transfer
else if(strcmp(path, "/api/wallet/transfer") == 0) {
    if (!json) {
        send_response(c, "400 Bad Request", "{\"error\":\"invalid_json\"}");
        return;
    }

    cJSON *from = cJSON_GetObjectItem(json, "from");
    cJSON *to = cJSON_GetObjectItem(json, "to");
    cJSON *amount = cJSON_GetObjectItem(json, "amount");

    if (!from || !to || !amount) {
        send_response(c, "400 Bad Request", "{\"error\":\"missing_fields\"}");
        cJSON_Delete(json);
        return;
    }

    int result = zl_wallet_transfer(db,
        cJSON_GetStringValue(from),
        cJSON_GetStringValue(to),
        cJSON_GetNumberValue(amount));

    response = cJSON_CreateObject();
    if (result == 0) {
        cJSON_AddStringToObject(response, "status", "success");
        cJSON_AddStringToObject(response, "from", cJSON_GetStringValue(from));
        cJSON_AddStringToObject(response, "to", cJSON_GetStringValue(to));
        cJSON_AddNumberToObject(response, "amount", cJSON_GetNumberValue(amount));
    } else if (result == -2) {
        cJSON_AddStringToObject(response, "error", "sender_not_found");
    } else if (result == -3) {
        cJSON_AddStringToObject(response, "error", "insufficient_balance");
    } else {
        cJSON_AddStringToObject(response, "error", "transfer_failed");
    }
}
```

---

*Complete Function Reference*  
*Last Updated: 2025-09-01*  
*Total Functions: 50+*  
*Implementation: C/SQLite*
