# Changelog

All notable changes to this project will be documented in this file.

## [v1.0.0] - 2026-03-10

### Added
- **Microservices Architecture**:
  - `gateway`: API Gateway with proxying and auth middleware.
  - `auth-service`: User registration, login, and JWT handling.
  - `wallet-service`: Wallet creation, balance management, and freezing logic.
  - `transaction-service`: Full transaction lifecycle (Deposit, Withdraw, Transfer) with ACID-like properties.
  - `notification-service`: RabbitMQ consumer for email notifications.
  - `admin-service`: Administrative actions (Ban, Freeze).
- **Infrastructure**:
  - Docker Compose setup for all services + Postgres (port 5435), Redis, RabbitMQ.
  - `shared` library for common database, security, and messaging code.
- **Documentation**:
  - `README.md`: Main project overview.
  - `docker-docs.md`: Guide for running with Docker.
  - `local-docs.md`: Guide for running locally.
  - `walkthrough.md`: Detailed project walkthrough.
- **CI/CD**:
  - GitHub Actions workflow (`ci.yml`) for automated testing.
- **Developer Tools**:
  - `local-install.sh`: Setup script.
  - `local-run.sh`: Local runner script.
  - `local-test.sh`: Local test runner.
