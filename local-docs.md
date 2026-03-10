# Local Run & Test Guide

This guide details how to run the services and tests directly on your local machine using the provided helper scripts.

## 🚀 Quick Start

We have provided shell scripts to automate the setup, running, and testing of the application locally.

### 1. Installation

Run the install script to create a virtual environment (`venv`) and install all dependencies:

```bash
./local-install.sh
```

### 2. Running the Full Stack

To start all microservices locally (Auth, Wallet, Transaction, Notification, Admin, Gateway) along with the necessary infrastructure (Postgres, Redis, RabbitMQ via Docker):

```bash
./local-run.sh
```

- Services will be started in the background.
- **API Gateway**: `http://localhost:8000`
- **Auth Service**: `http://localhost:8001`
- **Wallet Service**: `http://localhost:8002`
- **Transaction Service**: `http://localhost:8003`
- **Admin Service**: `http://localhost:8004`
- **Infrastructure**: Postgres (5435), Redis (6379), RabbitMQ (5672)

**To stop functionality**: Press `Ctrl+C` in the terminal where the script is running. It will kill all background processes.

### 3. Running Tests

To run the unit tests for all services:

```bash
./local-test.sh
```

---

## 🛠️ Manual Setup (Under the Hood)

If you prefer to run things manually or debug a specific service, here is what the scripts do.

### Prerequisites
- **Python 3.12**
- **Docker Compose** (for infrastructure)

### 1. Infrastructure
Start the database and message broker:
```bash
docker compose up -d postgres redis rabbitmq
```

### 2. Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r gateway/requirements.txt
# ... install other requirements as needed
```

### 3. Running a Single Service (e.g., Auth)
You must export the necessary environment variables and run `uvicorn`.

```bash
export DATABASE_URL="postgresql://user:password@localhost:5435/auth_db"
export RABBITMQ_URL="amqp://guest:guest@localhost:5672/"
export PYTHONPATH=$PYTHONPATH:$(pwd)

uvicorn auth-service.main:app --port 8001 --reload
```
