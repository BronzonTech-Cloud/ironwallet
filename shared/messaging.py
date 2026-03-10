import json
import time

import pika

from shared.config import settings


def get_rabbitmq_connection():
    params = pika.URLParameters(settings.RABBITMQ_URL)
    retries = 5
    for i in range(retries):
        try:
            connection = pika.BlockingConnection(params)
            return connection
        except pika.exceptions.AMQPConnectionError:
            if i == retries - 1:
                raise
            time.sleep(2 * (i + 1))
            print(f"Retrying RabbitMQ connection ({i+1}/{retries})...")


def publish_event(routing_key: str, message: dict):
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue=routing_key, durable=True)
    channel.basic_publish(
        exchange="",
        routing_key=routing_key,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ),
    )
    connection.close()


def consume_event(queue_name: str, callback):
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print(f" [*] Waiting for messages in {queue_name}. To exit press CTRL+C")
    channel.start_consuming()
