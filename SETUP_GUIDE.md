# 🚀 Complete Setup & Deployment Guide

## Prerequisites Installation

### 1. Install Node.js and npm
```bash
# Check if already installed
node --version
npm --version

# If not installed, download from https://nodejs.org/
# Or use package manager:
sudo apt update
sudo apt install nodejs npm
```

### 2. Install Ganache CLI
```bash
npm install -g ganache
```

### 3. Install Truffle Framework
```bash
npm install -g truffle
```

### 4. Install Python 3 and pip
```bash
# Check if already installed
python3 --version
pip3 --version

# If not installed:
sudo apt update
sudo apt install python3 python3-pip
```

## Step-by-Step Deployment

### Step 1: Start Ganache Blockchain

Open a new terminal and run:
```bash
ganache --port 8545 --networkId 1337 --chainId 1337
```

**Important**: Keep this terminal running! You should see:
- 10 available accounts with addresses
- Private keys for each account
- Listening on 127.0.0.1:8545

**Copy one of the private keys** - you'll need it in Step 3.

### Step 2: Compile and Deploy Smart Contract

Open a new terminal:
```bash
cd exam-paper-blockchain/blockchain

# Compile the smart contract
truffle compile

# Deploy to Ganache
truffle migrate --network development
```

**Expected Output**:
```
Compiling your contracts...
===========================
> Compiling ./contracts/SecureExamPaper.sol

...

✅ SecureExamPaper contract deployed successfully!
📍 Contract Address: 0x... (COPY THIS ADDRESS)
```

**Copy the contract address** - you'll need it in Step 3.

### Step 3: Configure Backend

Edit `backend/config/blockchain.json`:
```json
{
  "rpc_url": "http://127.0.0.1:8545",
  "chain_id": 1337,
  "contract_address": "PASTE_CONTRACT_ADDRESS_HERE",
  "private_key": "PASTE_GANACHE_PRIVATE_KEY_HERE",
  "abi_path": "../blockchain/build/contracts/SecureExamPaper.json"
}
```

Replace:
- `PASTE_CONTRACT_ADDRESS_HERE` with the contract address from Step 2
- `PASTE_GANACHE_PRIVATE_KEY_HERE` with a private key from Step 1 (without 0x prefix)

### Step 4: Install Python Dependencies

```bash
cd exam-paper-blockchain/backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Start Backend Server

```bash
# Make sure you're in the backend directory
cd exam-paper-blockchain/backend

# Activate virtual environment if not already active
source venv/bin/activate

# Start Flask server
python3 app.py
```

**Expected Output**:
```
✅ Connected to blockchain at http://127.0.0.1:8545
📊 Chain ID: 1337
👤 Using account: 0x...
✅ Contract loaded at 0x...
✅ All services initialized successfully

============================================================
🎓 BLOCKCHAIN EXAM PAPER VERIFICATION SYSTEM
============================================================
📡 API Server starting...
🌐 Access at: http://localhost:5000
...
```

**Keep this terminal running!**

### Step 6: Serve Frontend

Open a new terminal:
```bash
cd exam-paper-blockchain/frontend

# Start simple HTTP server
python3 -m http.server 8000
```

**Expected Output**:
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

### Step 7: Access the Application

Open your web browser and navigate to:
```
http://localhost:8000/login.html
```

## Testing the Complete Workflow

### Test 1: Admin Upload (SET Portal)

1. **Login as Admin**
   - Register No: `ADMIN001`
   - Password: `admin123`
   - Click "Login"

2. **Upload Exam Paper**
   - Select a PDF file (create a sample PDF if needed)
   - College ID: `COL001`
   - Subject Code: `CS101`
   - Exam Date/Time: Select a future date/time
   - Principal Email: `principal@college.edu`
   - Click "Encrypt & Store on Blockchain"

3. **Verify Success**
   - Watch the progress steps (AES encryption, RSA encryption, blockchain storage)
   - Note the Paper ID (you'll need this for principal verification)
   - Check that all steps show green checkmarks

### Test 2: Principal Verification (GET Portal)

1. **Logout and Login as Principal**
   - Logout from admin
   - Register No: `PRIN001`
   - Password: `principal123`

2. **Verify Paper (Step 1)**
   - Enter the Paper ID from admin upload
   - Click "Fetch Paper Details"
   - Review the paper information
   - Check time-lock status

3. **Decrypt Paper (Step 2)**
   - Switch to "Step 2: Decrypt Paper" tab
   - Enter Paper ID
   - Upload the encrypted package file from `backend/uploads/encrypted_paper_X.json`
   - College ID: `COL001`
   - Click "Decrypt & Download PDF"

4. **Verify Success**
   - Watch decryption progress
   - See green tick validation
   - PDF should download automatically
   - Verify the downloaded PDF matches the original

## Troubleshooting

### Issue: "Failed to connect to Ganache blockchain"
**Solution**: Make sure Ganache is running on port 8545
```bash
ganache --port 8545 --networkId 1337 --chainId 1337
```

### Issue: "Contract ABI not found"
**Solution**: Make sure you compiled and deployed the contract
```bash
cd blockchain
truffle compile
truffle migrate --network development
```

### Issue: "Invalid session" or authentication errors
**Solution**: Clear browser localStorage and login again
- Open browser console (F12)
- Run: `localStorage.clear()`
- Refresh page and login

### Issue: "Time-lock: LOCKED"
**Solution**: The exam date/time hasn't been reached yet. Either:
- Wait until the scheduled time
- Upload a new paper with an earlier exam time for testing

### Issue: Backend import errors
**Solution**: Make sure all dependencies are installed
```bash
cd backend
pip install -r requirements.txt
```

### Issue: "Port already in use"
**Solution**: Kill the process using the port
```bash
# For port 5000 (backend)
lsof -ti:5000 | xargs kill -9

# For port 8000 (frontend)
lsof -ti:8000 | xargs kill -9
```

## Terminal Summary

You should have **4 terminals running**:

1. **Terminal 1**: Ganache blockchain
   ```bash
   ganache --port 8545 --networkId 1337 --chainId 1337
   ```

2. **Terminal 2**: Backend Flask server
   ```bash
   cd backend
   python3 app.py
   ```

3. **Terminal 3**: Frontend HTTP server
   ```bash
   cd frontend
   python3 -m http.server 8000
   ```

4. **Terminal 4**: For running commands (compile, migrate, etc.)

## Production Deployment Notes

For production deployment:

1. **Use a real Ethereum network** (Sepolia testnet or mainnet)
2. **Secure private keys** using environment variables or key management services
3. **Enable real email service** in `email_service.py`
4. **Add HTTPS** for frontend and backend
5. **Implement proper session management** with Redis or database
6. **Add rate limiting** to API endpoints
7. **Conduct security audit** of smart contract
8. **Use proper database** instead of JSON files for user storage

## Success Checklist

✅ Ganache running on port 8545  
✅ Smart contract compiled and deployed  
✅ Contract address updated in blockchain.json  
✅ Private key updated in blockchain.json  
✅ Python dependencies installed  
✅ Backend server running on port 5000  
✅ Frontend server running on port 8000  
✅ Can login as admin  
✅ Can upload and encrypt paper  
✅ Can login as principal  
✅ Can verify and decrypt paper  
✅ Green tick validation appears  

---

**Congratulations!** Your blockchain exam verification system is now fully operational! 🎉
