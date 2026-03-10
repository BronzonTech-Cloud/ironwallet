import time

import requests

BASE_URL = "http://localhost:8000"


def test_flow():
    # 1. Register User
    print("Registering User...")
    user_data = {
        "email": f"test_{int(time.time())}@example.com",
        "name": "Test User",
        "phone": f"123456{int(time.time())}",
        "password": "password123",
    }
    resp = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    assert resp.status_code == 200
    user_id = resp.json()["id"]
    print(f"User ID: {user_id}")

    # 2. Login
    print("Logging in...")
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Logged in.")

    # 3. Create Wallet
    print("Creating Wallet...")
    wallet_data = {"user_id": user_id, "currency": "USD"}
    resp = requests.post(f"{BASE_URL}/wallet/create", json=wallet_data, headers=headers)
    assert resp.status_code == 200
    wallet_id = resp.json()["id"]
    print(f"Wallet ID: {wallet_id}")

    # 4. Deposit
    print("Depositing Money...")
    deposit_data = {"type": "DEPOSIT", "to_wallet": wallet_id, "amount": 1000.0}
    resp = requests.post(
        f"{BASE_URL}/transaction/deposit", json=deposit_data, headers=headers
    )
    print(resp.text)
    assert resp.status_code == 200

    # 5. Check Balance
    print("Checking Balance...")
    resp = requests.get(f"{BASE_URL}/wallet/{wallet_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["balance"] == 1000.0
    print("Balance verified.")

    print("Integration Test Passed!")


if __name__ == "__main__":
    try:
        test_flow()
    except Exception as e:
        print(f"Test Failed: {e}")
