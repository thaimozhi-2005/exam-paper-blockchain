#!/bin/bash
# Stop any existing processes on the project ports
echo "Cleaning up existing processes..."
lsof -ti:5000,8000,8545 | xargs -r kill -9
sleep 2

# Start Ganache with a fixed mnemonic
echo "Starting Ganache..."
ganache --server.port 8545 --chain.networkId 1337 --chain.chainId 1337 --wallet.mnemonic "honest amazing essence logic match provide actual method setup target allow mammal" > ganache.log 2>&1 &
GANACHE_PID=$!
sleep 5

# Check if Ganache started
if ! ps -p $GANACHE_PID > /dev/null; then
    echo "Failed to start Ganache. Check ganache.log"
    cat ganache.log
    exit 1
fi

echo "Deploying contract..."
cd blockchain
npx truffle migrate --network development --reset > migrate.log 2>&1
if [ $? -ne 0 ]; then
    echo "Migration failed. Check blockchain/migrate.log"
    cat migrate.log
    kill $GANACHE_PID
    exit 1
fi

# Extract contract address
CONTRACT_ADDRESS=$(grep "contract address:" migrate.log | tail -n 1 | awk '{print $NF}')
echo "Contract Address: $CONTRACT_ADDRESS"

# Private key for the mnemonic (Account 0)
# For the mnemonic "honest amazing essence logic match provide actual method setup target allow mammal":
# Account 0: 0x6E4973318999E74f8376999E74f8376999E74f83 (Just an example, I'll extract it from log if possible)
# Actually, ganache output contains the private keys.
PRIVATE_KEY=$(grep -A 20 "Private Keys" ../ganache.log | grep "(0)" | awk '{print $NF}')
echo "Private Key: $PRIVATE_KEY"

# Update blockchain.json
cd ..
cat > backend/config/blockchain.json << EOF
{
  "rpc_url": "http://127.0.0.1:8545",
  "chain_id": 1337,
  "contract_address": "$CONTRACT_ADDRESS",
  "private_key": "$PRIVATE_KEY",
  "abi_path": "../blockchain/build/contracts/SecureExamPaper.json"
}
EOF

echo "Starting Backend..."
cd backend
source venv/bin/activate
nohup python3 app.py > backend.log 2>&1 &
BACKEND_PID=$!
sleep 5

# Check if Backend started
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "Failed to start Backend. Check backend/backend.log"
    cat backend.log
    kill $GANACHE_PID
    exit 1
fi

echo "Starting Frontend..."
cd ../frontend
nohup python3 -m http.server 8000 > frontend.log 2>&1 &
FRONTEND_PID=$!

echo "Successfully started everything!"
echo "Ganache PID: $GANACHE_PID"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "You can now access the app at http://localhost:8000/login.html"
