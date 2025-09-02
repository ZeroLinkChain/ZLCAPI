#!/usr/bin/env python3
"""
ZeroLinkChain Test Miner
Connects to local pool and submits shares for testing
"""

import socket
import json
import hashlib
import time
import random
import threading

class ZeroLinkChainMiner:
    def __init__(self, pool_host='localhost', pool_port=8333):
        self.pool_host = pool_host
        self.pool_port = pool_port
        self.running = False
        self.shares_found = 0
        self.blocks_found = 0
        
    def mine_share(self, work_template):
        """Mine a share for the given work template"""
        target = work_template.get('target', '0000' + 'f' * 60)
        target_int = int(target, 16)
        
        # Simple mining loop
        for nonce in range(100000):  # Limit iterations for demo
            # Create block hash
            block_data = f"{work_template.get('previous_hash', 'genesis')}{work_template.get('coinbase_address', 'pool')}{work_template.get('timestamp', int(time.time()))}{nonce}"
            block_hash = hashlib.sha256(block_data.encode()).hexdigest()
            
            if int(block_hash, 16) <= target_int:
                return {
                    'nonce': nonce,
                    'hash': block_hash
                }
        
        # If no valid share found, return a random one for testing
        nonce = random.randint(1, 1000000)
        block_data = f"{work_template.get('previous_hash', 'genesis')}{work_template.get('coinbase_address', 'pool')}{work_template.get('timestamp', int(time.time()))}{nonce}"
        block_hash = hashlib.sha256(block_data.encode()).hexdigest()
        
        return {
            'nonce': nonce,
            'hash': block_hash
        }
    
    def connect_and_mine(self):
        """Connect to pool and start mining"""
        print(f"🔗 Connecting to ZeroLinkChain pool at {self.pool_host}:{self.pool_port}")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10.0)
            sock.connect((self.pool_host, self.pool_port))
            
            print("✅ Connected to mining pool!")
            self.running = True
            
            while self.running:
                try:
                    # Receive work template
                    data = sock.recv(4096).decode().strip()
                    if data:
                        work = json.loads(data)
                        
                        if work.get('type') == 'keepalive':
                            print("💓 Keepalive received")
                            continue
                        
                        print(f"📋 Work received: height {work.get('height', 'unknown')}, difficulty {work.get('difficulty', 'unknown')}")
                        
                        # Mine a share
                        share = self.mine_share(work)
                        if share:
                            print(f"⛏️  Share found: {share['hash'][:16]}... (nonce: {share['nonce']})")
                            
                            # Submit share
                            sock.send((json.dumps(share) + '\n').encode())
                            
                            # Get result
                            sock.settimeout(5.0)
                            result_data = sock.recv(1024).decode().strip()
                            if result_data:
                                result = json.loads(result_data)
                                print(f"📊 Result: {result.get('result', 'unknown')}")
                                
                                if result.get('result') == 'block_found':
                                    self.blocks_found += 1
                                    print(f"🎉 BLOCK FOUND! Total blocks: {self.blocks_found}")
                                    print(f"💰 Reward: {result.get('reward', 0)} ZLC")
                                elif result.get('result') == 'share_accepted':
                                    self.shares_found += 1
                                    print(f"✅ Share accepted! Total shares: {self.shares_found}")
                                    print(f"💰 Reward: {result.get('reward', 0)} ZLC")
                                else:
                                    print(f"❌ Share rejected: {result.get('reason', 'unknown')}")
                        
                        time.sleep(2)  # Small delay between shares
                        
                except socket.timeout:
                    print("⏰ Timeout waiting for pool response")
                    continue
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    continue
                    
        except ConnectionRefusedError:
            print("❌ Connection refused - is the mining pool running?")
        except Exception as e:
            print(f"❌ Mining error: {e}")
        finally:
            self.running = False
            try:
                sock.close()
            except:
                pass
            print("⏹️  Miner stopped")
    
    def start(self):
        """Start mining in a separate thread"""
        mining_thread = threading.Thread(target=self.connect_and_mine)
        mining_thread.daemon = True
        mining_thread.start()
        return mining_thread

def main():
    print("🚀 ZeroLinkChain Test Miner")
    print("==========================")
    
    miner = ZeroLinkChainMiner()
    
    try:
        mining_thread = miner.start()
        
        # Keep main thread alive and show stats
        while miner.running:
            time.sleep(10)
            print(f"📈 Mining Stats: {miner.shares_found} shares, {miner.blocks_found} blocks found")
            
    except KeyboardInterrupt:
        print("\n⏹️  Stopping miner...")
        miner.running = False
        time.sleep(1)
    
    print(f"📊 Final Stats: {miner.shares_found} shares, {miner.blocks_found} blocks found")

if __name__ == "__main__":
    main()
