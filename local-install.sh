#!/bin/bash
set -e

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing shared dependencies..."
# If there were a shared requirements.txt, we'd install it.
# We'll install service requirements.

echo "Installing Service Dependencies..."
pip install -r gateway/requirements.txt
pip install -r auth-service/requirements.txt
pip install -r wallet-service/requirements.txt
pip install -r transaction-service/requirements.txt
pip install -r notification-service/requirements.txt
pip install -r admin-service/requirements.txt

echo "Installing Test Dependencies..."
pip install pytest httpx requests

echo "------------------------------------------------"
echo "Installation Complete!"
echo "To activate venv, run: source venv/bin/activate"
