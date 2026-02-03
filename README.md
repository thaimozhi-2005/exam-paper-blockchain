# 🎓 Blockchain Exam Paper Verification System

A secure, decentralized exam paper distribution system using **Ethereum blockchain**, **AES-256 + RSA-4096 encryption**, and **time-lock mechanisms**.

## 🌟 Features

### Security Layers
- **AES-256 Encryption**: Military-grade content encryption
- **RSA-4096 Encryption**: Secure key encryption
- **Blockchain Storage**: Immutable record keeping on Ethereum
- **Time-Lock Mechanism**: Prevents early access to exam papers
- **Hash Verification**: Tamper detection using SHA-256
- **Visual Validation**: Green tick confirmation system

### User Interfaces
1. **Admin Portal (SET.html)**: University administrators upload and encrypt exam papers
2. **Principal Portal (GET.html)**: College principals verify and decrypt papers
3. **Authentication System**: Role-based access control

## 📁 Project Structure

```
exam-paper-blockchain/
├── blockchain/
│   ├── contracts/
│   │   └── SecureExamPaper.sol          # Smart contract
│   ├── migrations/
│   │   └── 1_deploy_secure_exam.js      # Deployment script
│   └── truffle-config.js                # Truffle configuration
│
├── backend/
│   ├── app.py                           # Flask REST API
│   ├── web3_client.py                   # Blockchain connection
│   ├── contract_loader.py               # Contract interface
│   ├── crypto_utils.py                  # AES + RSA encryption
│   ├── hash_utils.py                    # SHA-256 hashing
│   ├── auth_service.py                  # Authentication
│   ├── email_service.py                 # Email delivery
│   ├── paper_service.py                 # Business logic
│   ├── config/
│   │   └── blockchain.json              # Configuration
│   └── requirements.txt                 # Python dependencies
│
└── frontend/
    ├── login.html                       # Login page
    ├── set.html                         # Admin portal
    ├── get.html                         # Principal portal
    ├── css/
    │   └── style.css                    # Styling
    └── js/
        ├── login.js                     # Login logic
        ├── set.js                       # Admin logic
        └── get.js                       # Principal logic
```

## 🚀 Quick Start

### Prerequisites
- Node.js (v14+)
- Python 3.8+
- Ganache (for local blockchain)
- Truffle Framework

### Installation

1. **Install Ganache**
```bash
npm install -g ganache
```

2. **Install Truffle**
```bash
npm install -g truffle
```

3. **Install Python Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

### Deployment

1. **Start Ganache**
```bash
ganache --port 8545 --networkId 1337 --chainId 1337
```

2. **Deploy Smart Contract**
```bash
cd blockchain
truffle compile
truffle migrate --network development
```

3. **Update Configuration**
   - Copy the deployed contract address
   - Copy a private key from Ganache
   - Update `backend/config/blockchain.json`

4. **Start Backend**
```bash
cd backend
python3 app.py
```

5. **Serve Frontend**
```bash
cd frontend
python3 -m http.server 8000
```

6. **Access Application**
   - Open browser: `http://localhost:8000/login.html`

## 👥 Default Credentials

### Admin (University)
- Register No: `ADMIN001`
- Password: `admin123`

### Principal (College)
- Register No: `PRIN001`
- Password: `principal123`

## 📖 Usage Workflow

### Admin Workflow (SET Portal)
1. Login as admin
2. Upload PDF exam paper
3. Enter college ID, subject code, exam date/time, principal email
4. System encrypts PDF with AES-256
5. System encrypts AES key with RSA-4096
6. Metadata stored on blockchain
7. Encrypted package emailed to principal

### Principal Workflow (GET Portal)
1. Login as principal
2. Enter Paper ID from email
3. Verify paper details from blockchain
4. Check time-lock status
5. Upload encrypted package file
6. System verifies time-lock
7. System decrypts with RSA private key
8. System decrypts PDF with AES key
9. Hash verification confirms authenticity
10. Green tick validation displayed
11. Download verified PDF

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ADMIN (University)                        │
│  1. Upload PDF                                               │
│  2. AES-256 Encrypt Content                                  │
│  3. RSA-4096 Encrypt AES Key                                 │
│  4. SHA-256 Hash Generation                                  │
│  5. Blockchain Storage (Immutable)                           │
│  6. Email Encrypted Package                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   BLOCKCHAIN (Ethereum)                      │
│  • Document Hash                                             │
│  • Encrypted AES Key                                         │
│  • Metadata (College, Subject, Exam Time)                    │
│  • Time-Lock Enforcement                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  PRINCIPAL (College)                         │
│  1. Receive Encrypted Package                                │
│  2. Time-Lock Verification                                   │
│  3. Fetch Data from Blockchain                               │
│  4. RSA Decrypt AES Key                                      │
│  5. AES Decrypt PDF                                          │
│  6. Hash Verification                                        │
│  7. Green Tick Validation                                    │
│  8. Download Verified PDF                                    │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| Blockchain | Ethereum (Ganache Local) |
| Smart Contract | Solidity ^0.8.19 |
| Backend | Python + Flask |
| Blockchain Library | Web3.py |
| Encryption | PyCryptodome (AES-256 + RSA-4096) |
| Frontend | HTML5 + CSS3 + JavaScript |
| Development | Truffle Framework |

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/login` | User authentication |
| POST | `/api/register` | User registration |
| POST | `/api/logout` | User logout |
| POST | `/api/admin/store-paper` | Upload & encrypt paper |
| GET | `/api/principal/verify-paper/<id>` | Fetch paper details |
| POST | `/api/principal/decrypt-paper` | Decrypt & download |
| GET | `/api/paper/<id>` | Get public metadata |
| GET | `/api/stats` | Blockchain statistics |
| GET | `/api/health` | Health check |

## 🎯 Key Highlights

✅ **Complete Security**: 3-layer encryption (AES + RSA + Blockchain)  
✅ **Time-Lock Mechanism**: Prevents unauthorized early access  
✅ **Visual Validation**: Green tick system for authenticity proof  
✅ **Immutable Records**: Blockchain ensures tamper-proof storage  
✅ **User-Friendly UI**: Modern, responsive design  
✅ **Academic Project Ready**: Suitable for final year projects  

## 📝 License

This project is created for educational purposes.

## 👨‍💻 Author

Blockchain Exam Verification System - Final Year Project

---

**Note**: This is a demonstration system using a local blockchain (Ganache). For production deployment, use a test network (Sepolia, Goerli) or mainnet with proper security audits.
