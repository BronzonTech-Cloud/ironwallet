# IronWallet

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0+-009688.svg)](https://fastapi.tiangolo.com/)

A comprehensive microservices-based banking wallet system (Mini Wave/PayPal clone) built with **Python FastAPI**, **Docker**, and **PostgreSQL**.

## 🏗️ Architecture

The system consists of 6 microservices:
1.  **API Gateway**: Public entry point, handles auth and routing.
2.  **Auth Service**: User registration and JWT authentication.
3.  **Wallet Service**: Manage wallets, balances, and freezing.
4.  **Transaction Service**: Handles deposits, withdrawals, and transfers (ACID compliance & locking).
5.  **Notification Service**: Consumes events (RabbitMQ) to send emails.
6.  **Admin Service**: Administrative actions (Ban, Freeze, View Txns).

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.12+ (for local dev)

### Quick Start (Docker)
1.  **Configure Environment**: Copy the example environment file and adjust if necessary:
    ```bash
    cp .env.example .env
    ```
2.  **Run Services**: Run the entire stack in detached mode:
    ```bash
    docker compose up --build -d
    ```

3.  **Wait for Ready**: Wait **10-15 seconds** for databases and RabbitMQ to fully initialize before accessing the API.
See [Docker Guide](docker-docs.md) for details.

### Local Development
Run services locally with our helper scripts:
```bash
./local-install.sh
./local-run.sh
```
See [Local Guide](local-docs.md) for details.

## 🧪 Testing

### Integration Tests
Ensure the stack is running via Docker, wait 15 seconds, and then run:
```bash
python3 integration_test.py
```

### Unit Tests
Run unit tests for all services:
```bash
./local-test.sh
```

## 📚 Documentation
- [Docker Deployment Guide](docker-docs.md)
- [Local Development Guide](local-docs.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)
- [API Documentation](http://localhost:8000/docs) (served by Gateway once running)

## 🛠️ Tech Stack
- **Language**: Python 3.12
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Messaging**: RabbitMQ
- **Caching**: Redis
- **Containerization**: Docker & Docker Compose

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
