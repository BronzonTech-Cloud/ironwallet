# Docker Run & Test Guide

This guide details how to run the **IronWallet API** and its tests using Docker.

## 🐳 1. Running the System

To start the entire microservices stack (Gateway, 5 Services, Postgres, Redis, RabbitMQ):

```bash
docker compose up --build
```

- **API Gateway**: `http://localhost:8000`
- **PostgreSQL**: `localhost:5435`
- **Redis**: `localhost:6379`
- **RabbitMQ Dashboard**: `http://localhost:15672` (guest/guest)

To stop the services:
```bash
docker compose down
```
To stop and remove volumes (reset databases):
```bash
docker compose down -v
```

## 🧪 2. Running Tests

### End-to-End Integration Test
This test runs from your host machine against the running Docker stack.

1. Ensure the stack is up (`docker compose up`).
2. Install `requests` locally if not present:
   ```bash
   pip install requests
   ```
3. Run the script:
   ```bash
   python integration_test.py
   ```

### Running Unit Tests Inside Containers
You can run the unit tests (pytest) directly inside the containerized services.

**Auth Service Tests:**
```bash
docker compose exec auth-service pytest
```

**Wallet Service Tests:**
```bash
docker compose exec wallet-service pytest
```

**Transaction Service Tests:**
```bash
docker compose exec transaction-service pytest
```

*(Note: Ensure you have `pytest` and `httpx` installed in the services or add them to requirements.txt if they are missing from the Docker image. Currently, they are included in `requirements.txt` implicitly or explicitly.)*
