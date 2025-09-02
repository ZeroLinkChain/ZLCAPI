#!/usr/bin/env python3
"""
ZeroLinkChain Node Service
Hosts a blockchain node for network participation and block data distribution
"""

import os
import sys
import time
import json
import hashlib
import socket
import threading
import requests
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/zerolinkchain-node.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ZLC-Node')

class ZeroLinkChainNode:
    def __init__(self, data_dir="/var/lib/zerolinkchain/node", port=8334, api_port=8335):
        self.data_dir = data_dir
        self.port = port
        self.api_port = api_port
        self.blockchain_file = os.path.join(data_dir, "blockchain.dat")
        self.peers = set()
        self.blocks = []
        self.api_base = "https://zerolinkchain.com/api"
        self.running = False
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        logger.info(f"ZeroLinkChain Node initialized")
        logger.info(f"P2P Port: {port}, API Port: {api_port}")
        logger.info(f"Data directory: {data_dir}")
    
    def load_blockchain(self):
        """Load blockchain data from file"""
        try:
            if os.path.exists(self.blockchain_file):
                with open(self.blockchain_file, 'rb') as f:
                    data = f.read()
                    logger.info(f"Loaded blockchain: {len(data)} bytes")
                    return data
            else:
                logger.info("No local blockchain found, will sync from network")
                return b''
        except Exception as e:
            logger.error(f"Failed to load blockchain: {e}")
            return b''
    
    def save_blockchain(self, data):
        """Save blockchain data to file"""
        try:
            with open(self.blockchain_file, 'wb') as f:
                f.write(data)
            logger.info(f"Blockchain saved: {len(data)} bytes")
        except Exception as e:
            logger.error(f"Failed to save blockchain: {e}")
    
    def sync_with_network(self):
        """Sync blockchain with the network"""
        try:
            # Get blockchain stats
            response = requests.get(f"{self.api_base}/miner/stats", timeout=10)
            if response.status_code == 200:
                stats = response.json()
                logger.info(f"Network height: {stats['height']}, difficulty: {stats['difficulty']}")
                
                # Get integrity status
                response = requests.get(f"{self.api_base}/integrity/status", timeout=10)
                if response.status_code == 200:
                    integrity = response.json()
                    logger.info(f"Chain integrity: {integrity['chain_integrity']}")
                    
                    # Simulate blockchain sync (in production, would download actual blocks)
                    self.simulate_blockchain_data(stats['height'])
                    
        except Exception as e:
            logger.warning(f"Network sync failed: {e}")
    
    def simulate_blockchain_data(self, height):
        """Simulate blockchain data for testing"""
        # Create simulated block data
        blocks_data = b''
        for i in range(height + 1):
            block = {
                'height': i,
                'hash': hashlib.sha256(f"block_{i}_{time.time()}".encode()).hexdigest(),
                'timestamp': int(time.time()) - (height - i) * 600,  # 10 min blocks
                'transactions': []
            }
            block_json = json.dumps(block).encode()
            blocks_data += len(block_json).to_bytes(4, 'big') + block_json
        
        self.save_blockchain(blocks_data)
        logger.info(f"Simulated blockchain with {height + 1} blocks")
    
    def handle_peer_connection(self, conn, addr):
        """Handle P2P peer connection"""
        peer_id = f"{addr[0]}:{addr[1]}"
        logger.info(f"Peer connected: {peer_id}")
        self.peers.add(peer_id)
        
        try:
            while self.running:
                # Send node info
                node_info = {
                    'type': 'node_info',
                    'version': '1.0.0',
                    'height': len(self.blocks),
                    'peers': len(self.peers),
                    'timestamp': time.time()
                }
                
                info_json = json.dumps(node_info) + '\n'
                conn.send(info_json.encode())
                
                # Wait for peer messages
                conn.settimeout(30.0)
                try:
                    data = conn.recv(1024).decode().strip()
                    if data:
                        try:
                            message = json.loads(data)
                            self.handle_peer_message(peer_id, message)
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid message from {peer_id}")
                            
                except socket.timeout:
                    # Send keepalive
                    keepalive = json.dumps({'type': 'keepalive'}) + '\n'
                    conn.send(keepalive.encode())
                    
        except Exception as e:
            logger.warning(f"Peer {peer_id} disconnected: {e}")
        finally:
            conn.close()
            self.peers.discard(peer_id)
            logger.info(f"Peer disconnected: {peer_id}")
    
    def handle_peer_message(self, peer_id, message):
        """Handle messages from peers"""
        msg_type = message.get('type')
        
        if msg_type == 'get_blocks':
            # Peer requesting blocks
            start_height = message.get('start_height', 0)
            logger.info(f"Peer {peer_id} requesting blocks from height {start_height}")
            
        elif msg_type == 'new_block':
            # Peer announcing new block
            block_data = message.get('block')
            logger.info(f"New block announced by {peer_id}: {block_data.get('hash', 'unknown')}")
            
        elif msg_type == 'ping':
            # Respond to ping
            logger.debug(f"Ping from {peer_id}")
    
    def start_p2p_server(self):
        """Start P2P server for peer connections"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', self.port))
        server_socket.listen(10)
        
        logger.info(f"P2P server listening on port {self.port}")
        
        while self.running:
            try:
                conn, addr = server_socket.accept()
                # Handle each peer in a separate thread
                peer_thread = threading.Thread(
                    target=self.handle_peer_connection,
                    args=(conn, addr)
                )
                peer_thread.daemon = True
                peer_thread.start()
                
            except Exception as e:
                if self.running:
                    logger.error(f"P2P server error: {e}")
                    time.sleep(1)
        
        server_socket.close()
    
    def get_node_stats(self):
        """Get node statistics"""
        blockchain_size = 0
        if os.path.exists(self.blockchain_file):
            blockchain_size = os.path.getsize(self.blockchain_file)
        
        return {
            'node_id': hashlib.sha256(f"node_{self.port}".encode()).hexdigest()[:16],
            'version': '1.0.0',
            'uptime': time.time() - getattr(self, 'start_time', time.time()),
            'peers_connected': len(self.peers),
            'blockchain_size': blockchain_size,
            'blocks_count': len(self.blocks),
            'p2p_port': self.port,
            'api_port': self.api_port,
            'data_directory': self.data_dir
        }

class NodeAPIHandler(BaseHTTPRequestHandler):
    """HTTP API handler for node"""
    
    def __init__(self, node, *args, **kwargs):
        self.node = node
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/stats':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            stats = self.node.get_node_stats()
            self.wfile.write(json.dumps(stats, indent=2).encode())
            
        elif self.path == '/peers':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            peers_list = list(self.node.peers)
            self.wfile.write(json.dumps({'peers': peers_list}).encode())
            
        elif self.path == '/blockchain':
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.end_headers()
            
            blockchain_data = self.node.load_blockchain()
            self.wfile.write(blockchain_data)
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"API: {format % args}")

def create_api_handler(node):
    """Create API handler with node reference"""
    def handler(*args, **kwargs):
        return NodeAPIHandler(node, *args, **kwargs)
    return handler

class ZeroLinkChainNodeService:
    def __init__(self):
        self.node = ZeroLinkChainNode()
        self.start_time = time.time()
    
    def start_api_server(self):
        """Start HTTP API server"""
        handler = create_api_handler(self.node)
        api_server = HTTPServer(('0.0.0.0', self.node.api_port), handler)
        
        logger.info(f"API server listening on port {self.node.api_port}")
        
        while self.node.running:
            try:
                api_server.handle_request()
            except Exception as e:
                if self.node.running:
                    logger.error(f"API server error: {e}")
                    time.sleep(1)
    
    def run_service(self):
        """Run node as a service"""
        logger.info("Starting ZeroLinkChain Node Service")
        self.node.running = True
        self.node.start_time = self.start_time
        
        # Load existing blockchain
        self.node.load_blockchain()
        
        # Sync with network
        self.node.sync_with_network()
        
        # Start P2P server in a separate thread
        p2p_thread = threading.Thread(target=self.node.start_p2p_server)
        p2p_thread.daemon = True
        p2p_thread.start()
        
        # Start API server in a separate thread
        api_thread = threading.Thread(target=self.start_api_server)
        api_thread.daemon = True
        api_thread.start()
        
        # Main service loop
        while True:
            try:
                # Log node statistics every 60 seconds
                stats = self.node.get_node_stats()
                logger.info(f"Node Stats: {stats['peers_connected']} peers, "
                          f"{stats['blockchain_size']} bytes blockchain, "
                          f"{stats['uptime']:.0f}s uptime")
                
                # Periodic network sync
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    self.node.sync_with_network()
                
                time.sleep(60)
                
            except KeyboardInterrupt:
                logger.info("Node service stopped by user")
                self.node.running = False
                break
            except Exception as e:
                logger.error(f"Service error: {e}")
                time.sleep(10)

def main():
    """Main service entry point"""
    node_service = ZeroLinkChainNodeService()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "stats":
            stats = node_service.node.get_node_stats()
            print(json.dumps(stats, indent=2))
            
        elif command == "sync":
            print("Syncing with network...")
            node_service.node.sync_with_network()
            print("Sync completed")
            
        else:
            print("Usage: zerolinkchain_node.py [stats|sync]")
    else:
        # Run as service
        node_service.run_service()

if __name__ == "__main__":
    main()
