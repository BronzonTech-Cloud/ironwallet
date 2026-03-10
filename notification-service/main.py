import json
import threading

from shared.logging_utils import get_logger
from shared.messaging import consume_event

logger = get_logger("notification-service")


def send_email(to_email: str, subject: str, message: str):
    # Mock sending email
    logger.info(f"-------- EMAIL SENT --------")
    logger.info(f"To: {to_email}")
    logger.info(f"Subject: {subject}")
    logger.info(f"Message: {message}")
    logger.info(f"----------------------------")


def process_user_registered(ch, method, properties, body):
    data = json.loads(body)
    logger.info(f"Received user.registered: {data}")
    send_email(
        data["email"], "Welcome to IronWallet", f"Hello {data['name']}, welcome!"
    )


def process_transaction_completed(ch, method, properties, body):
    data = json.loads(body)
    logger.info(f"Received transaction.completed: {data}")
    # In a real app, we'd look up user email based on wallet ID via Auth Service
    send_email(
        "user@example.com",
        "Transaction Completed",
        f"Transaction {data['id']} completed. Amount: {data['amount']}",
    )


def process_wallet_frozen(ch, method, properties, body):
    data = json.loads(body)
    logger.info(f"Received wallet.frozen: {data}")
    send_email(
        "user@example.com",
        "Wallet Frozen",
        f"Your wallet {data['wallet_id']} has been frozen.",
    )


def start_consuming(queue, callback):
    consume_event(queue, callback)


if __name__ == "__main__":
    logger.info("Starting Notification Service...")

    # We need multiple threads or connection configs to consume from multiple queues easily,
    # or just bind multiple routing keys to one queue.
    # For simplicity, I'll start one thread per queue or just one sequential consumtion if I use one queue.
    # But usually topics are better. Here I used direct queues in `consume_event`.
    # Let's just create threads for simplicity.

    t1 = threading.Thread(
        target=start_consuming, args=("user.registered", process_user_registered)
    )
    t2 = threading.Thread(
        target=start_consuming,
        args=("transaction.completed", process_transaction_completed),
    )
    t3 = threading.Thread(
        target=start_consuming, args=("wallet.frozen", process_wallet_frozen)
    )

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()
