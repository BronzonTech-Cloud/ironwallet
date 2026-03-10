#!/bin/bash

# Ensure venv is activated
source venv/bin/activate || { echo "Virtual environment not found. Run local-install.sh first."; exit 1; }

export PYTHONPATH=$PWD

echo "Running Unit Tests..."

echo ">> Auth Service"
# Set dummy DB URL for tests that might import models but if tests use Mock, it's fine.
# If tests connect to DB, we need valid URL.
export DATABASE_URL="postgresql://user:password@localhost:5435/auth_db"
pytest auth-service/test_main.py

echo ">> Wallet Service"
export DATABASE_URL="postgresql://user:password@localhost:5435/wallet_db"
export REDIS_URL="redis://localhost:6379/1"
pytest wallet-service/test_main.py

echo ">> Transaction Service"
export DATABASE_URL="postgresql://user:password@localhost:5435/transaction_db"
pytest transaction-service/test_main.py

echo "------------------------------------------------"
echo "Tests Complete."
