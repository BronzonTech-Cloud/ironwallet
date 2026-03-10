#!/bin/bash

# Ensure venv is activated
source venv/bin/activate || { echo "Virtual environment not found. Run local-install.sh first."; exit 1; }

# Add current directory to PYTHONPATH so "shared" module is found
export PYTHONPATH=$PWD

# Infrastructure Ports (Must be running via Docker Compose or locally)
export POSTGRES_PORT=5435
export REDIS_PORT=6379
export RABBITMQ_PORT=5672

echo "Starting Infrastructure (Postgres, Redis, RabbitMQ) via Docker..."
docker compose up -d postgres redis rabbitmq

echo "Waiting for infrastructure..."
sleep 5

# Common Envs
export REDIS_URL="redis://localhost:6379/0"
export RABBITMQ_URL="amqp://guest:guest@localhost:5672/"
export JWT_SECRET_KEY="supersecretkey"

# --- 1. Auth Service (Port 8001) ---
echo "Starting Auth Service on Port 8001..."
export DATABASE_URL="postgresql://user:password@localhost:$POSTGRES_PORT/auth_db"
uvicorn auth-service.main:app --host 0.0.0.0 --port 8001 &
AUTH_PID=$!

# --- 2. Wallet Service (Port 8002) ---
echo "Starting Wallet Service on Port 8002..."
export DATABASE_URL="postgresql://user:password@localhost:$POSTGRES_PORT/wallet_db"
export REDIS_URL="redis://localhost:6379/1"
uvicorn wallet-service.main:app --host 0.0.0.0 --port 8002 &
WALLET_PID=$!

# --- 3. Transaction Service (Port 8003) ---
echo "Starting Transaction Service on Port 8003..."
export DATABASE_URL="postgresql://user:password@localhost:$POSTGRES_PORT/transaction_db"
export REDIS_URL="redis://localhost:6379/2"
export WALLET_SERVICE_URL="http://localhost:8002"
uvicorn transaction-service.main:app --host 0.0.0.0 --port 8003 &
TXN_PID=$!

# --- 4. Notification Service (Background) ---
echo "Starting Notification Service..."
export RABBITMQ_URL="amqp://guest:guest@localhost:5672/"
# We run this in background
python3 notification-service/main.py &
NOTIFY_PID=$!

# --- 5. Admin Service (Port 8004) ---
echo "Starting Admin Service on Port 8004..."
export DATABASE_URL_AUTH="postgresql://user:password@localhost:$POSTGRES_PORT/auth_db"
export DATABASE_URL_WALLET="postgresql://user:password@localhost:$POSTGRES_PORT/wallet_db"
export DATABASE_URL_TRANSACTION="postgresql://user:password@localhost:$POSTGRES_PORT/transaction_db"
uvicorn admin-service.main:app --host 0.0.0.0 --port 8004 &
ADMIN_PID=$!

# --- 6. API Gateway (Port 8000) ---
echo "Starting API Gateway on Port 8000..."
export AUTH_SERVICE_URL="http://localhost:8001"
export WALLET_SERVICE_URL="http://localhost:8002"
export TRANSACTION_SERVICE_URL="http://localhost:8003"
export ADMIN_SERVICE_URL="http://localhost:8004"
export REDIS_URL="redis://localhost:6379/0"

uvicorn gateway.main:app --host 0.0.0.0 --port 8000 &
GATEWAY_PID=$!

echo "--------------------------------------------------------"
echo "All services started!"
echo "Gateway running at http://localhost:8000"
echo "Press Ctrl+C to stop all services."
echo "--------------------------------------------------------"

# Cleanup function
cleanup() {
    echo "Stopping all services..."
    kill $AUTH_PID $WALLET_PID $TXN_PID $NOTIFY_PID $ADMIN_PID $GATEWAY_PID
    exit
}

trap cleanup SIGINT

wait
