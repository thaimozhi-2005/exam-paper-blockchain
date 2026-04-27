# 🎓 Secure Exam Paper Blockchain System

A decentralized, end-to-end encrypted platform for secure distribution and verification of examination papers using Ethereum Blockchain technology.

## 🌟 Overview

This project ensures the integrity and security of examination papers by leveraging blockchain for immutability and AES-256 for military-grade encryption. It eliminates the risk of paper leaks and unauthorized access during the transit from the Board to the Examination Centers.

### Key Features
- **Immutability**: Once a paper hash is stored on the blockchain, it cannot be tampered with.
- **End-to-End Encryption**: Papers are AES-256 encrypted. Keys are securely managed and only accessible to authorized Principals.
- **Verification System**: Automated verification ensures that the downloaded paper matches the official version stored on the blockchain.
- **Role-Based Access**: Specialized interfaces for Administrators (Board) and Principals (Colleges).
- **Desktop Application**: A professional, cross-platform desktop wrapper for ease of use.

---

## 🛠️ Technology Stack

- **Blockchain**: Ethereum (Solidity Smart Contracts)
- **Development Framework**: Truffle Suite & Ganache
- **Backend**: Python 3 (Flask REST API)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Desktop Wrapper**: PyWebView
- **Security**: PyCryptodome (AES-256, RSA, SHA-256)
- **Web3 Interface**: Web3.py

---

## 🚀 Setup & Installation

Please choose the guide matching your Operating System for detailed, step-by-step instructions:

| Operating System | Guide Link |
| :--- | :--- |
| **🪟 Windows** | [Windows Setup Guide (README_WINDOWS.md)](./README_WINDOWS.md) |
| **🐧 Ubuntu / Linux** | [Ubuntu Setup Guide (README_UBUNTU.md)](./README_UBUNTU.md) |

---

## 📂 Quick Project Structure

- `blockchain/`: Contains Solidity contracts, migrations, and build artifacts.
- `backend/`: Flask API handling encryption, user management, and blockchain interaction.
- `frontend/`: Web interface components (HTML, CSS, JS).
- `desktop_app.py`: The GUI wrapper that launches the native desktop window.
- `start_all.sh` / `launch_app.sh`: Automated deployment and execution scripts.

---

## 🔐 Security Workflow
1. **Admin** uploads a PDF and specifies the Subject/College.
2. The system **Encrypts** the PDF using a unique AES key.
3. The **Hash** of the PDF is recorded on the **Blockchain**.
4. An encrypted package is sent to the **Principal's Email**.
5. **Principal** logs in, verifies the paper identity, and decrypts it using their secure credentials.

---

## 👥 Authors
- **Thaimozhi** - *Initial Work & Architecture*

---
*Developed for secure academic examination management.*
