# 🐧 Ubuntu Setup Guide: Exam Paper Blockchain System

This guide provides step-by-step instructions for deploying and running the project on **Ubuntu (Linux)**.

---

## 1. Prerequisites (Installation)

Update your system and install the required base tools:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-venv python3-pip nodejs npm
```

### Install GUI Dependencies
Ubuntu requires specific libraries to run the `pywebview` desktop window:
```bash
sudo apt install -y python3-gi python3-gi-cairo gir1.2-webkit2-4.1
```

---

## 2. Clone the Project

```bash
git clone <your-repository-url>
cd "exam paper blockchain"
```

---

## 3. Install Blockchain Packages (Ganache & Truffle)

1.  Install Ganache and Truffle globally using npm:
    ```bash
    sudo npm install -g ganache truffle
    ```
2.  Install local project dependencies:
    ```bash
    cd blockchain
    npm install
    cd ..
    ```

---

## 4. Setup Python & Libraries

1.  Create a virtual environment:
    ```bash
    python3 -m venv venv
    ```
2.  Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```
3.  Install **all required packages**:
    ```bash
    # Core Libraries (Flask, Web3, Cryptography)
    pip install Flask==3.0.0 web3==6.15.1 pycryptodome==3.19.1 flask-cors==4.0.0 python-dotenv==1.0.0
    
    # Desktop GUI Library
    pip install pywebview
    ```

---

## 5. Deployment & RPC Settings

We have provided an **Automated Script** for Ubuntu that handles Ganache start, contract migration, and configuration sync automatically.

### Automated Way (Recommended)
```bash
chmod +x launch_app.sh
./launch_app.sh
```

### Manual Way
If you prefer running step-by-step:
1.  **Start Ganache**: `ganache --port 8545 &`
2.  **Deploy Contract**: `cd blockchain && truffle migrate --network development && cd ..`
3.  **Run App**: `python3 desktop_app.py`

---

## 🚀 Advanced Settings

### RPC & Network Configuration
The connection between the Backend and the Blockchain is managed in:
`backend/config/blockchain.json`

By default, it uses:
- **RPC URL**: `http://127.0.0.1:8545`
- **Network ID**: 1337

### Email Protocol (SMTP)
To configure the real email sender (Gmail), modify:
`backend/email_service.py`
- Set `self.demo_mode = False`
- Enter your `SENDER_EMAIL` and `SENDER_PASSWORD` (App Password).

---

## 🛠️ Troubleshooting (Ubuntu)

- **Port already in use**: Run `fuser -k 5000/tcp 8545/tcp` to clear stuck processes.
- **Permission Denied**: Ensure you ran `chmod +x` on the `.sh` scripts.
- **Webview Error**: Verify that you installed the `gir1.2-webkit2-4.1` package mentioned in Step 1.
