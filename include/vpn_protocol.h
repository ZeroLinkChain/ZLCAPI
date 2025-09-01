#ifndef ZEROLINKCHAIN_VPN_PROTOCOL_H
#define ZEROLINKCHAIN_VPN_PROTOCOL_H

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "zerolinkchain_core.h"

// VPN Session structure (simple host<->client context)
typedef struct {
    uint32_t session_id;
    uint32_t host_id;
    uint32_t client_id;
    uint32_t sequence;
    time_t last_active;
    uint64_t bytes_sent;
    uint64_t bytes_received;
    char remote_ip[16];
    uint16_t remote_port;
    int is_active;
} vpn_session_t;

// VPN Route structure (aligned with implementation in vpn_protocol.c)
typedef struct {
    char route_id[64];
    uint32_t hop_count;
    uint32_t total_latency;
    uint32_t min_bandwidth;
    uint8_t asn_diversity;
    char exit_country[3];
    int is_active;
} vpn_route_t;

// Function declarations
int init_vpn_protocol(void);
void cleanup_vpn_protocol(void);

// Session management
vpn_session_t* create_session(uint32_t host_id, uint32_t client_id);
void close_session(uint32_t session_id);
vpn_session_t* get_session(uint32_t session_id);

// Route management
vpn_route_t* create_route(const char* destination, uint32_t host_id);
void close_route(const char* route_id);
vpn_route_t* get_route(const char* route_id);
vpn_route_t* find_best_route(const char* destination);

// Stats and monitoring
void get_vpn_stats(size_t *total_hosts, size_t *active_hosts, size_t *active_sessions_count,
                   uint64_t *total_bytes_sent, uint64_t *total_bytes_received);
int get_active_sessions(void);
int get_active_routes(void);

// Confidential multi-hop routing & lightweight encryption (XOR over SHA256 key)
// NOTE: Full PGP per-hop onion encryption will use pgp_crypto in future iteration.
// These helper functions enforce:
//  - Minimum 3 hops (entry, >=1 middle, exit)
//  - Entry & exit must be confidential-capable (reliability>=0.8, bandwidth>=100 Mbps)
//  - ASN diversity for middle hops when possible

// Build a confidential route (exit_country optional, pass NULL for any)
// Returns 0 on success, negative on error.
int build_confidential_route(const char *exit_country, vpn_route_t **out_route);

// Encrypt / decrypt payload using derived stream key: SHA256(wallet_privkey||route_id)
// Caller ensures output buffer >= len.
int vpn_encrypt_with_route(const char *route_id, const uint8_t *plaintext, size_t len, uint8_t *ciphertext);
int vpn_decrypt_with_route(const char *route_id, const uint8_t *ciphertext, size_t len, uint8_t *plaintext);

// Load (or reload) wallet private key from environment (ZLC_WALLET_PRIVKEY).
// Returns pointer to internal static buffer.
const char *vpn_get_wallet_privkey(void);

#endif // ZEROLINKCHAIN_VPN_PROTOCOL_H
