#!/bin/bash
# ============================================
# Blockchain Exam Verification System
# Desktop Application Launcher
# ============================================
# This script is called by the .desktop file
# It starts Ganache, the backend, and opens the app

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure Node/NVM is in path for desktop launch
export PATH="$HOME/.nvm/versions/node/v20.19.0/bin:$PATH"

echo "🔗 Starting Blockchain Exam Verification System..."

# 1. Clean up stale processes (Silent)
echo "🧹 Cleaning up existing processes..."
fuser -k 5000/tcp 8000/tcp 8545/tcp >/dev/null 2>&1
sleep 2

# Clear logs to ensure fresh state and accurate grep
> ganache_launch.log
> launch.log
> frontend_launch.log
cd blockchain && > migrate.log && cd ..

# 2. Start Ganache with a fixed mnemonic and PERSISTENT database
echo "⏳ Starting Ganache Blockchain (Persistent)..."
DB_DIR="$SCRIPT_DIR/blockchain/ganache_db"
mkdir -p "$DB_DIR"

# Log DB status
if [ "$(ls -A $DB_DIR)" ]; then
    echo "📦 Existing database found. Loading history..."
else
    echo "🆕 New database initialized."
fi

# Use explicit node_modules path if available for consistency
GANACHE_BIN="$SCRIPT_DIR/blockchain/node_modules/.bin/ganache"
if [ ! -f "$GANACHE_BIN" ]; then
    GANACHE_BIN="ganache"
fi

nohup "$GANACHE_BIN" --port 8545 --networkId 1337 --database.dbPath "$DB_DIR" --mnemonic "honest amazing essence logic match provide actual method setup target allow mammal" > "$SCRIPT_DIR/ganache_launch.log" 2>&1 &
sleep 6

# 3. Deploy Contract (Only if needed)
echo "⛓️  Checking Smart Contract status..."
cd "$SCRIPT_DIR/blockchain"
# DON'T use --reset here to keep data
npx truffle migrate --network development > migrate.log 2>&1

# 4. Extract details and Update backend config
# First, try to get address from migrate.log (if it just deployed)
NEW_ADDRESS=$(grep "contract address:" migrate.log | tail -n 1 | awk '{print $NF}')

# If migrate.log doesn't have it (Up to date), try to find it in the build artifacts
if [ -z "$NEW_ADDRESS" ]; then
    echo "🔍 Contract up to date. Fetching existing address..."
    # Parse the address from the Truffle build artifact (most reliable for persistence)
    NEW_ADDRESS=$(python3 -c "import json; print(json.load(open('build/contracts/SecureExamPaper.json'))['networks']['1337']['address'])" 2>/dev/null)
fi

# Extract private key from ganache log
PRIVATE_KEY=$(grep -A 20 "Private Keys" "$SCRIPT_DIR/ganache_launch.log" | grep "(0)" | awk '{print $NF}')

if [ ! -z "$NEW_ADDRESS" ]; then
    echo "📝 Contract matched at: $NEW_ADDRESS"
    echo "📝 Syncing configuration..."
    
    # Auto-detect this machine's LAN IP (so Windows clients can connect)
    LAN_IP=$(ip route get 1.1.1.1 | grep -oP '(?<=src\s)\S+' | head -1)
    if [ -z "$LAN_IP" ]; then
        LAN_IP="127.0.0.1"  # fallback to localhost
    fi
    echo "🌐 Server LAN IP detected: $LAN_IP"
    
    cat > "$SCRIPT_DIR/backend/config/blockchain.json" << EOF
{
  "rpc_url": "http://127.0.0.1:8545",
  "server_ip": "$LAN_IP",
  "chain_id": 1337,
  "contract_address": "$NEW_ADDRESS",
  "private_key": "$PRIVATE_KEY",
  "abi_path": "../blockchain/build/contracts/SecureExamPaper.json"
}
EOF
    echo "✅ Config written. Windows clients connect via: http://$LAN_IP:5000"
else
    echo "❌ Error: Could not find Contract Address. Please check migrate.log"
    ls -l build/contracts/SecureExamPaper.json
fi

# 5. Launch the Desktop App (Starts Backend + Frontend)

# 6. Launch the Desktop App Window
echo "🚀 Launching Desktop Application Window..."
cd "$SCRIPT_DIR"
# CRITICAL: Use the specific venv that has pywebview installed
PYTHON_PATH="/home/thaimozhi2005/venv/bin/python3"

if [ ! -f "$PYTHON_PATH" ]; then
    # Fallback/Debug if path changed
    PYTHON_PATH="python3"
fi

"$PYTHON_PATH" "$SCRIPT_DIR/desktop_app.py" >> "$SCRIPT_DIR/launch.log" 2>&1

