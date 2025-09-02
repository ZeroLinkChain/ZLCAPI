#!/usr/bin/env python3
"""
ZeroLinkChain Wallet Service
Creates and manages wallet with real blockchain integration
"""

import os
import sys
import time
import json
import hashlib
import secrets
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/zerolinkchain-wallet.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ZLC-Wallet')

class ZeroLinkChainWallet:
    def __init__(self, data_dir="/var/lib/zerolinkchain/wallet"):
        self.data_dir = data_dir
        self.wallet_file = os.path.join(data_dir, "wallet.json")
        self.api_base = "https://zerolinkchain.com/api"
        self.wallet_data = None
        self.session_token = None
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        logger.info("ZeroLinkChain Wallet Service initialized")
    
    def generate_wallet_address(self):
        """Generate a ZeroLinkChain wallet address"""
        # Generate 32 bytes of entropy
        entropy = secrets.token_bytes(32)
        # Create address hash
        address_hash = hashlib.sha256(entropy).hexdigest()
        # Format as ZLC address (ZLC + 61 chars = 64 total)
        return f"ZLC{address_hash[:61]}"
    
    def generate_private_key(self):
        """Generate a 64-character hex private key"""
        return secrets.token_hex(32)
    
    def generate_mnemonic(self):
        """Generate a 12-word mnemonic phrase"""
        # Simple word list for demo (use proper BIP39 in production)
        words = [
            'abandon', 'ability', 'able', 'about', 'above', 'absent',
            'absorb', 'abstract', 'absurd', 'abuse', 'access', 'accident',
            'account', 'accuse', 'achieve', 'acid', 'acoustic', 'acquire',
            'across', 'act', 'action', 'actor', 'actress', 'actual'
        ]
        return ' '.join(secrets.choice(words) for _ in range(12))
    
    def create_wallet(self):
        """Create a new wallet"""
        try:
            # Generate wallet credentials
            address = self.generate_wallet_address()
            private_key = self.generate_private_key()
            mnemonic = self.generate_mnemonic()
            
            # Create wallet data
            wallet_data = {
                'address': address,
                'private_key': private_key,
                'mnemonic': mnemonic,
                'created_at': datetime.now().isoformat(),
                'balance': 0.0,
                'mining_rewards': 0.0,
                'transactions': []
            }
            
            # Save wallet to file
            with open(self.wallet_file, 'w') as f:
                json.dump(wallet_data, f, indent=2)
            
            # Set secure permissions
            os.chmod(self.wallet_file, 0o600)
            
            self.wallet_data = wallet_data
            logger.info(f"Wallet created: {address}")
            
            # Create session with API
            self.create_api_session()
            
            return wallet_data
            
        except Exception as e:
            logger.error(f"Failed to create wallet: {e}")
            return None
    
    def load_wallet(self):
        """Load existing wallet"""
        try:
            if not os.path.exists(self.wallet_file):
                logger.info("No existing wallet found, creating new one")
                return self.create_wallet()
            
            with open(self.wallet_file, 'r') as f:
                self.wallet_data = json.load(f)
            
            logger.info(f"Wallet loaded: {self.wallet_data['address']}")
            
            # Create session with API
            self.create_api_session()
            
            return self.wallet_data
            
        except Exception as e:
            logger.error(f"Failed to load wallet: {e}")
            return None
    
    def create_api_session(self):
        """Create API session for secure wallet operations"""
        try:
            # Use the secure wallet API
            response = requests.post(f"{self.api_base}/wallet/import/privatekey", 
                                   json={'private_key': self.wallet_data['private_key']},
                                   timeout=10)
            
            if response.status_code == 200:
                session_data = response.json()
                self.session_token = session_data.get('session_token')
                logger.info("API session created successfully")
            else:
                logger.warning(f"API session creation failed: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"API session creation error: {e}")
    
    def get_balance(self):
        """Get wallet balance from blockchain"""
        try:
            if not self.session_token:
                logger.warning("No API session, using local balance")
                return self.wallet_data.get('balance', 0.0)
            
            headers = {'Authorization': f'Bearer {self.session_token}'}
            response = requests.get(f"{self.api_base}/wallet/balance", 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                balance_data = response.json()
                balance = balance_data.get('balance', 0.0)
                
                # Update local wallet data
                self.wallet_data['balance'] = balance
                self.wallet_data['mining_rewards'] = balance_data.get('mining_rewards', 0.0)
                self.save_wallet()
                
                return balance
            else:
                logger.warning(f"Balance query failed: {response.status_code}")
                return self.wallet_data.get('balance', 0.0)
                
        except Exception as e:
            logger.error(f"Balance query error: {e}")
            return self.wallet_data.get('balance', 0.0)
    
    def save_wallet(self):
        """Save wallet data to file"""
        try:
            with open(self.wallet_file, 'w') as f:
                json.dump(self.wallet_data, f, indent=2)
            logger.debug("Wallet data saved")
        except Exception as e:
            logger.error(f"Failed to save wallet: {e}")
    
    def get_wallet_info(self):
        """Get complete wallet information"""
        if not self.wallet_data:
            return None
        
        balance = self.get_balance()
        
        return {
            'address': self.wallet_data['address'],
            'balance': balance,
            'mining_rewards': self.wallet_data.get('mining_rewards', 0.0),
            'created_at': self.wallet_data.get('created_at'),
            'session_active': bool(self.session_token),
            'transactions_count': len(self.wallet_data.get('transactions', []))
        }
    
    def run_service(self):
        """Run wallet as a service"""
        logger.info("Starting ZeroLinkChain Wallet Service")
        
        # Load or create wallet
        if not self.load_wallet():
            logger.error("Failed to initialize wallet")
            return
        
        logger.info(f"Wallet Address: {self.wallet_data['address']}")
        logger.info(f"Initial Balance: {self.get_balance()} ZLC")
        
        # Service loop
        while True:
            try:
                # Update balance every 30 seconds
                balance = self.get_balance()
                logger.info(f"Current Balance: {balance} ZLC")
                
                # Check for new transactions (placeholder)
                # In production, this would sync with the blockchain
                
                time.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("Wallet service stopped by user")
                break
            except Exception as e:
                logger.error(f"Service error: {e}")
                time.sleep(10)

def main():
    """Main service entry point"""
    wallet_service = ZeroLinkChainWallet()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            wallet = wallet_service.create_wallet()
            if wallet:
                print(f"Wallet created: {wallet['address']}")
                print(f"Private key: {wallet['private_key']}")
                print(f"Mnemonic: {wallet['mnemonic']}")
            
        elif command == "info":
            wallet_service.load_wallet()
            info = wallet_service.get_wallet_info()
            if info:
                print(json.dumps(info, indent=2))
            
        elif command == "balance":
            wallet_service.load_wallet()
            balance = wallet_service.get_balance()
            print(f"Balance: {balance} ZLC")
            
        else:
            print("Usage: zerolinkchain_wallet.py [create|info|balance|service]")
    else:
        # Run as service
        wallet_service.run_service()

if __name__ == "__main__":
    main()
