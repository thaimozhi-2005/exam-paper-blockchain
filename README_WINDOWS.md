# 🪟 Windows Setup Guide: Exam Paper Blockchain System

This guide provides step-by-step instructions for deploying and running the project on **Windows 10/11**.

---

## 1. Prerequisites (Installation)

Before starting, install the following software:

1.  **Git**: [Download and Install Git](https://git-scm.com/download/win).
2.  **Node.js (LTS)**: [Download and Install Node.js](https://nodejs.org/). (Needed for Ganache/Blockchain).
3.  **Python 3.10+**: [Download from Python.org](https://www.python.org/). 
    *   **⚠️ IMPORTANT**: Check the box **"Add Python to PATH"** during installation.

---

## 2. Clone the Project

Open **PowerShell** or **Command Prompt** and run:
```powershell
git clone <your-repository-url>
cd "exam paper blockchain"
```

---

## 3. Install Blockchain Packages (Ganache & Truffle)

We use Ganache as our local blockchain and Truffle for smart contract deployment.

1.  Open PowerShell as **Administrator**.
2.  Install Ganache and Truffle globally:
    ```powershell
    npm install -g ganache truffle
    ```
3.  Install local project dependencies:
    ```powershell
    cd blockchain
    npm install
    cd ..
    ```

---

## 4. Setup Python & Libraries

1.  Create a virtual environment to keep packages isolated:
    ```powershell
    python -m venv venv
    ```
2.  Activate the virtual environment:
    ```powershell
    .\venv\Scripts\activate
    ```
3.  Install **all required packages**:
    ```powershell
    # Core Libraries (Flask, Web3, Cryptography)
    pip install Flask==3.0.0 web3==6.15.1 pycryptodome==3.19.1 flask-cors==4.0.0 python-dotenv==1.0.0
    
    # Desktop GUI Library
    pip install pywebview
    ```

---

## 5. Configuration & RPC Settings

### A. Start the Local Blockchain (Ganache)
Run this in a **separate** terminal window and keep it open:
```powershell
ganache --port 8545 --chain.networkId 1337 --chain.chainId 1337 --mnemonic "honest amazing essence logic match provide actual method setup target allow mammal"
```

### B. Deploy Smart Contract
In your main terminal (where venv is active):
```powershell
cd blockchain
truffle migrate --network development --reset
cd ..
```

---

## 6. Running the Application

Once Ganache is running and the contract is deployed, start the system:

```powershell
# Ensure you are in the root directory and venv is active
python desktop_app.py
```

*   The **Admin Portal** will be available at: `http://localhost:5000/set.html`
*   The **Principal Portal** will be available at: `http://localhost:5000/get.html`

---

## 🛠️ Troubleshooting (Windows)

*   **Execution Policy Error**: If you cannot activate `venv`, run:
    `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
*   **Module Not Found**: Ensure you always run `.\venv\Scripts\activate` before starting the app.
*   **Port 5000 in use**: Open Task Manager, find any "Python" processes, and end them.
