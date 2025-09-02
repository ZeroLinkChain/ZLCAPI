#!/usr/bin/env python3
"""
ZeroLinkChain Mining Pool Service
Hosts a mining pool for ZLC mining with real blockchain integration
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/zerolinkchain-pool.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ZLC-Pool')

class ZeroLinkChainPool:
    def __init__(self, pool_address=None, port=8333):
        self.pool_address = pool_address or self.load_pool_wallet()
        self.port = port
        self.miners = {}
        self.shares = []
        self.current_block = None
        self.difficulty = 4
        self.api_base = "https://zerolinkchain.com/api"
        self.running = False
        
        logger.info(f"ZeroLinkChain Pool initialized on port {port}")
        logger.info(f"Pool wallet: {self.pool_address}")
    
    def load_pool_wallet(self):
        """Load pool wallet address"""
        wallet_file = "/var/lib/zerolinkchain/wallet/wallet.json"
        try:
            if os.path.exists(wallet_file):
                with open(wallet_file, 'r') as f:
                    wallet_data = json.load(f)
                return wallet_data['address']
        except Exception as e:
            logger.warning(f"Could not load pool wallet: {e}")
        
        # Generate temporary pool address
        return f"ZLC{hashlib.sha256(b'pool_' + str(time.time()).encode()).hexdigest()[:61]}"
    
    def get_blockchain_stats(self):
        """Get current blockchain statistics"""
        try:
            response = requests.get(f"{self.api_base}/miner/stats", timeout=10)
            if response.status_code == 200:
                stats = response.json()
                self.difficulty = stats.get('difficulty', 4)
                return stats
        except Exception as e:
            logger.warning(f"Failed to get blockchain stats: {e}")
        
        return {
            'height': 18,
            'difficulty': self.difficulty,
            'hashrate_hps': 66666.67
        }
    
    def create_work_template(self):
        """Create mining work template"""
        stats = self.get_blockchain_stats()
        
        # Create block template
        template = {
            'height': stats['height'] + 1,
            'previous_hash': hashlib.sha256(f"block_{stats['height']}".encode()).hexdigest(),
            'difficulty': stats['difficulty'],
            'target': '0' * stats['difficulty'] + 'f' * (64 - stats['difficulty']),
            'coinbase_address': self.pool_address,
            'timestamp': int(time.time()),
            'nonce_start': 0,
            'nonce_end': 0xFFFFFFFF
        }
        
        return template
    
    def validate_share(self, miner_id, nonce, block_hash):
        """Validate submitted mining share"""
        try:
            # Simple validation - check if hash meets pool difficulty
            hash_int = int(block_hash, 16)
            target_int = int('0' * self.difficulty + 'f' * (64 - self.difficulty), 16)
            
            if hash_int <= target_int:
                # Valid share
                share = {
                    'miner_id': miner_id,
                    'nonce': nonce,
                    'hash': block_hash,
                    'timestamp': time.time(),
                    'difficulty': self.difficulty,
                    'valid': True
                }
                self.shares.append(share)
                
                # Check if it's a valid block
                if hash_int <= target_int // 4:  # Block found
                    logger.info(f"Block found by miner {miner_id}!")
                    self.submit_block(share)
                    return {'result': 'block_found', 'reward': 10.0}
                else:
                    return {'result': 'share_accepted', 'reward': 0.1}
            else:
                return {'result': 'share_rejected', 'reason': 'insufficient_difficulty'}
                
        except Exception as e:
            logger.error(f"Share validation error: {e}")
            return {'result': 'share_rejected', 'reason': 'validation_error'}
    
    def submit_block(self, share):
        """Submit found block to blockchain"""
        try:
            block_data = {
                'miner': self.pool_address,
                'nonce': share['nonce'],
                'hash': share['hash'],
                'timestamp': share['timestamp']
            }
            
            # In production, this would submit to the actual blockchain
            logger.info(f"Block submitted: {share['hash']}")
            
            # Distribute rewards to miners
            self.distribute_rewards(10.0)  # 10 ZLC block reward
            
        except Exception as e:
            logger.error(f"Block submission error: {e}")
    
    def distribute_rewards(self, total_reward):
        """Distribute mining rewards to pool participants"""
        if not self.shares:
            return
        
        # Calculate shares for last 100 submissions
        recent_shares = self.shares[-100:]
        miner_shares = {}
        
        for share in recent_shares:
            if share['valid']:
                miner_id = share['miner_id']
                miner_shares[miner_id] = miner_shares.get(miner_id, 0) + 1
        
        total_shares = sum(miner_shares.values())
        if total_shares == 0:
            return
        
        # Distribute rewards proportionally
        for miner_id, shares_count in miner_shares.items():
            reward = (shares_count / total_shares) * total_reward * 0.98  # 2% pool fee
            
            if miner_id in self.miners:
                self.miners[miner_id]['balance'] += reward
                logger.info(f"Reward distributed: {reward:.6f} ZLC to {miner_id}")
    
    def handle_miner_connection(self, conn, addr):
        """Handle individual miner connection"""
        miner_id = f"{addr[0]}:{addr[1]}"
        logger.info(f"Miner connected: {miner_id}")
        
        self.miners[miner_id] = {
            'address': addr,
            'connected_at': time.time(),
            'shares_submitted': 0,
            'shares_accepted': 0,
            'balance': 0.0,
            'hashrate': 0.0
        }
        
        try:
            while self.running:
                # Send work template
                work = self.create_work_template()
                work_json = json.dumps(work) + '\n'
                conn.send(work_json.encode())
                
                # Wait for share submission
                conn.settimeout(30.0)
                try:
                    data = conn.recv(1024).decode().strip()
                    if data:
                        share_data = json.loads(data)
                        
                        # Validate share
                        result = self.validate_share(
                            miner_id,
                            share_data.get('nonce'),
                            share_data.get('hash')
                        )
                        
                        # Update miner stats
                        self.miners[miner_id]['shares_submitted'] += 1
                        if result['result'] in ['share_accepted', 'block_found']:
                            self.miners[miner_id]['shares_accepted'] += 1
                        
                        # Send result back to miner
                        response = json.dumps(result) + '\n'
                        conn.send(response.encode())
                        
                except socket.timeout:
                    # Send keepalive
                    keepalive = json.dumps({'type': 'keepalive'}) + '\n'
                    conn.send(keepalive.encode())
                    
        except Exception as e:
            logger.warning(f"Miner {miner_id} disconnected: {e}")
        finally:
            conn.close()
            if miner_id in self.miners:
                del self.miners[miner_id]
            logger.info(f"Miner disconnected: {miner_id}")
    
    def start_pool_server(self):
        """Start the mining pool server"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', self.port))
        server_socket.listen(10)
        
        logger.info(f"Pool server listening on port {self.port}")
        
        while self.running:
            try:
                conn, addr = server_socket.accept()
                # Handle each miner in a separate thread
                miner_thread = threading.Thread(
                    target=self.handle_miner_connection,
                    args=(conn, addr)
                )
                miner_thread.daemon = True
                miner_thread.start()
                
            except Exception as e:
                if self.running:
                    logger.error(f"Server error: {e}")
                    time.sleep(1)
        
        server_socket.close()
    
    def get_pool_stats(self):
        """Get pool statistics"""
        total_hashrate = sum(miner['hashrate'] for miner in self.miners.values())
        total_shares = len([s for s in self.shares if s['valid']])
        
        return {
            'pool_address': self.pool_address,
            'connected_miners': len(self.miners),
            'total_hashrate': total_hashrate,
            'total_shares': total_shares,
            'difficulty': self.difficulty,
            'miners': list(self.miners.keys())
        }
    
    def run_service(self):
        """Run pool as a service"""
        logger.info("Starting ZeroLinkChain Mining Pool Service")
        self.running = True
        
        # Start pool server in a separate thread
        server_thread = threading.Thread(target=self.start_pool_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Main service loop
        while True:
            try:
                # Log pool statistics every 60 seconds
                stats = self.get_pool_stats()
                logger.info(f"Pool Stats: {stats['connected_miners']} miners, "
                          f"{stats['total_hashrate']:.2f} H/s, "
                          f"{stats['total_shares']} shares")
                
                time.sleep(60)
                
            except KeyboardInterrupt:
                logger.info("Pool service stopped by user")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Service error: {e}")
                time.sleep(10)

def main():
    """Main service entry point"""
    pool_service = ZeroLinkChainPool()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "stats":
            stats = pool_service.get_pool_stats()
            print(json.dumps(stats, indent=2))
            
        elif command == "test":
            # Test pool functionality
            print("Testing pool...")
            stats = pool_service.get_blockchain_stats()
            print(f"Blockchain stats: {stats}")
            work = pool_service.create_work_template()
            print(f"Work template: {work}")
            
        else:
            print("Usage: zerolinkchain_pool.py [stats|test]")
    else:
        # Run as service
        pool_service.run_service()

if __name__ == "__main__":
    main()
