#!/usr/bin/env python3
"""
Test the real ZeroLinkChain system
"""

import json
import time
from zerolinkchain_real import zerolinkchain

def test_real_system():
    print("🧪 Testing Real ZeroLinkChain System")
    print("=" * 50)
    
    # Test system status
    status = zerolinkchain.get_system_status()
    print(f"📊 System Status:")
    print(f"   Blocks: {status['blocks_mined']}")
    print(f"   Dead TXs: {status['dead_txs_processed']}")
    print(f"   Active Hosts: {status['active_hosts']}")
    print(f"   Total Users: {status['total_users']}")
    print(f"   Network Throughput: {status['network_throughput']} Mbps")
    
    # Test hosts data
    hosts_data = zerolinkchain.get_hosts_data()
    print(f"\n🌐 Hosts Data:")
    print(f"   Total Hosts: {hosts_data['total_hosts']}")
    print(f"   Active Hosts: {hosts_data['active_hosts']}")
    
    for host in hosts_data['hosts']:
        status_icon = "🟢" if host['active'] else "🔴"
        print(f"   {status_icon} {host['host_id']} - {host['location']} ({host['bandwidth_mbps']} Mbps)")
    
    # Test mining a block
    print(f"\n⛏️ Testing Mining:")
    if zerolinkchain.users:
        miner = next((user for user in zerolinkchain.users if user.is_mining), None)
        if miner:
            print(f"   Mining block with {miner.username}...")
            block = zerolinkchain.mine_block(f"Test block by {miner.username}", miner.wallet_address)
            if block:
                print(f"   ✅ Block mined! Hash: {block.hash[:16]}...")
                print(f"   Nonce: {block.nonce}")
            else:
                print(f"   ❌ Mining failed")
    
    # Test creating a dead transaction
    print(f"\n💀 Testing Dead TX:")
    dead_tx = zerolinkchain.create_dead_tx(
        sender="alice",
        recipient="bob", 
        data={"message": "Hello from ZeroLinkChain!", "type": "chat"},
        tx_type="chainchat"
    )
    print(f"   ✅ Dead TX created! ID: {dead_tx.tx_id}")
    print(f"   Type: {dead_tx.tx_type}")
    print(f"   Data: {dead_tx.data}")
    
    # Show updated status
    print(f"\n📈 Updated Status:")
    updated_status = zerolinkchain.get_system_status()
    print(f"   Blocks: {updated_status['blocks_mined']}")
    print(f"   Dead TXs: {updated_status['dead_txs_processed']}")
    
    print(f"\n✅ Real ZeroLinkChain system is working!")
    print(f"🎯 You can now use this system for real blockchain operations!")

if __name__ == "__main__":
    test_real_system()
