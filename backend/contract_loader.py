"""
Contract Loader - Loads and interacts with the SecureExamPaper smart contract
"""

import json
import os

class ContractLoader:
    def __init__(self, web3_client, config_path='config/blockchain.json'):
        """Initialize contract loader"""
        self.w3_client = web3_client
        self.w3 = web3_client.w3
        self.account = web3_client.account
        
        # Load configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.contract_address = config['contract_address']
        
        # Load ABI from compiled contract
        abi_path = config.get('abi_path', '../blockchain/build/contracts/SecureExamPaper.json')
        
        if not os.path.exists(abi_path):
            raise Exception(f"Contract ABI not found at {abi_path}. Please compile and deploy the contract first.")
        
        with open(abi_path, 'r') as f:
            contract_json = json.load(f)
            self.abi = contract_json['abi']
        
        # Load contract
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.abi
        )
        
        print(f"✅ Contract loaded at {self.contract_address}")
    
    def store_paper(self, college_id, subject_code, document_hash, exam_datetime, encrypted_aes_key, principal_email):
        """
        Store exam paper on blockchain
        Returns: (paper_id, transaction_hash)
        """
        try:
            # Log parameters for debugging
            print(f"DEBUG: Storing paper...")
            print(f"  College: {college_id}")
            print(f"  Subject: {subject_code}")
            print(f"  Hash: {document_hash}")
            print(f"  Exam Time: {exam_datetime} (Block: {self.w3.eth.get_block('latest').timestamp})")
            
            # Build transaction
            txn = self.contract.functions.storePaper(
                college_id,
                subject_code,
                document_hash,
                exam_datetime,
                encrypted_aes_key,
                principal_email
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 1000000, # Increased gas
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(txn, private_key=self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt.status == 0:
                raise Exception("Transaction reverted on-chain. Check if paper with same hash exists or if exam time is invalid.")
            
            # Get paper ID from event logs
            paper_stored_event = self.contract.events.PaperStored().process_receipt(tx_receipt)
            
            if not paper_stored_event:
                # If transaction succeeded but event is missing, try to find paper ID by hash as fallback
                try:
                    # This is a bit expensive but helps in weird cases
                    total = self.get_total_papers()
                    for i in range(1, total + 1):
                        p = self.get_paper(i)
                        if p['documentHash'] == document_hash:
                            return i, tx_hash.hex()
                except:
                    pass
                raise Exception("Transaction succeeded but PaperStored event was not found in logs.")
            
            paper_id = paper_stored_event[0]['args']['paperId']
            return paper_id, tx_hash.hex()
            
        except Exception as e:
            print(f"❌ Blockchain Error: {str(e)}")
            raise Exception(f"Failed to store paper on blockchain: {str(e)}")
    
    def get_paper(self, paper_id):
        """
        Get paper details from blockchain
        Returns: dict with paper details
        """
        try:
            paper = self.contract.functions.getPaper(paper_id).call()
            
            return {
                'collegeId': paper[0],
                'subjectCode': paper[1],
                'documentHash': paper[2],
                'timestamp': paper[3],
                'owner': paper[4],
                'verified': paper[5],
                'examDateTime': paper[6],
                'encryptedAESKey': paper[7],
                'principalEmail': paper[8]
            }
        except Exception as e:
            raise Exception(f"Failed to get paper from blockchain: {str(e)}")
    
    def verify_paper(self, paper_id):
        """Mark paper as verified on blockchain"""
        try:
            txn = self.contract.functions.verifyPaper(paper_id).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(txn, private_key=self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return tx_hash.hex()
        except Exception as e:
            raise Exception(f"Failed to verify paper: {str(e)}")

    def reschedule_exam(self, paper_id, new_exam_datetime):
        """Update exam scheduled time on blockchain"""
        try:
            txn = self.contract.functions.rescheduleExam(paper_id, new_exam_datetime).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(txn, private_key=self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt.status == 0:
                raise Exception("Transaction reverted. Make sure you are the author and paper is not verified.")
                
            return tx_hash.hex()
        except Exception as e:
            raise Exception(f"Failed to reschedule exam: {str(e)}")
    
    def get_blockchain_time(self):
        """Get the current timestamp from the latest block (Consensus Time)"""
        try:
            # IMPORTANT: For local development (Ganache), the blockchain clock 
            # stops if no transactions occur. We force a sync with system time 
            # to ensure the "Real-World" experience where time actually moves.
            self.w3_client.sync_blockchain_time()
            return self.w3.eth.get_block('latest').timestamp
        except Exception as e:
            # Fallback to system time if blockchain is unreachable
            import time
            return int(time.time())

    def is_exam_time_reached(self, paper_id):
        """Check if exam time has been reached (time-lock)"""
        try:
            # Sync time before checking to ensure accurate development environment
            self.get_blockchain_time()
            return self.contract.functions.isExamTimeReached(paper_id).call()
        except Exception as e:
            raise Exception(f"Failed to check exam time: {str(e)}")
    
    def get_total_papers(self):
        """Get total number of papers stored"""
        return self.contract.functions.getTotalPapers().call()
    
    def does_hash_exist(self, document_hash):
        """Check if a document hash already exists"""
        return self.contract.functions.doesHashExist(document_hash).call()
