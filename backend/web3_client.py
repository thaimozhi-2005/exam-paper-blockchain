"""
Web3 Client - Manages connection to Ganache blockchain
"""

from web3 import Web3
import json
import os

class Web3Client:
    def __init__(self, config_path='config/blockchain.json'):
        """Initialize Web3 connection to Ganache"""
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Connect to Ganache
        self.w3 = Web3(Web3.HTTPProvider(self.config['rpc_url']))
        
        # Verify connection
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Ganache blockchain")
        
        print(f"✅ Connected to blockchain at {self.config['rpc_url']}")
        print(f"📊 Chain ID: {self.w3.eth.chain_id}")
        
        # Set default account
        self.account = self.w3.eth.account.from_key(self.config['private_key'])
        self.w3.eth.default_account = self.account.address
        
        print(f"👤 Using account: {self.account.address}")
        
    def get_account(self):
        """Get the current account address"""
        return self.account.address
    
    def get_balance(self, address=None):
        """Get ETH balance of an address"""
        if address is None:
            address = self.account.address
        balance_wei = self.w3.eth.get_balance(address)
        balance_eth = self.w3.from_wei(balance_wei, 'ether')
        return float(balance_eth)
    
    def send_transaction(self, transaction):
        """
        Send a transaction to the blockchain
        Handles nonce, gas estimation, signing, and receipt
        """
        try:
            # Get current nonce
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            # Add nonce to transaction
            transaction['nonce'] = nonce
            
            # Estimate gas if not provided
            if 'gas' not in transaction:
                transaction['gas'] = self.w3.eth.estimate_gas(transaction)
            
            # Add gas price if not provided
            if 'gasPrice' not in transaction:
                transaction['gasPrice'] = self.w3.eth.gas_price
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, 
                private_key=self.config['private_key']
            )
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            print(f"📤 Transaction sent: {tx_hash.hex()}")
            
            # Wait for receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            print(f"✅ Transaction confirmed in block {tx_receipt['blockNumber']}")
            
            return tx_receipt
            
        except Exception as e:
            print(f"❌ Transaction failed: {str(e)}")
            raise
    
    def get_transaction_receipt(self, tx_hash):
        """Get transaction receipt"""
        return self.w3.eth.get_transaction_receipt(tx_hash)
    
    def get_block_number(self):
        """Get current block number"""
        return self.w3.eth.block_number
    
    def get_block_timestamp(self):
        """Get current block timestamp"""
        block = self.w3.eth.get_block('latest')
        return block['timestamp']

    def sync_blockchain_time(self):
        """
        Force Ganache blockchain clock to sync with real system time.
        Only works on local development nodes (Ganache/Hardhat).
        """
        try:
            import time
            now = int(time.time())
            # Set the timestamp for the next block
            self.w3.provider.make_request('evm_setNextBlockTimestamp', [now])
            # Mine a block to apply the timestamp change
            self.w3.provider.make_request('evm_mine', [])
            return True
        except Exception as e:
            print(f"⚠️ Could not sync blockchain time: {str(e)}")
            return False
