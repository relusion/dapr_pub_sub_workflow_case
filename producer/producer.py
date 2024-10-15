"""
This app sends messages to a RabbitMQ exchange at regular intervals.

Environment Variables:
- MESSAGE_COUNT: Number of messages to send (default: 10).
- DELAY_BETWEEN_MESSAGES_SECONDS: Delay between sending messages in seconds (default: 3).
- RABBITMQ_CONNECTION_STRING: Connection string for RabbitMQ.

Functions:
- send_messages(): Establishes a connection to RabbitMQ, sends messages to a specified exchange, and closes the connection.

Usage:
Ensure the required environment variables are set before running the script. The script will send the specified number of messages to the RabbitMQ exchange with a delay between each message.
"""

from cloudevents.sdk.event import v1
from dotenv import load_dotenv
import pika
import time
import json
import os
import uuid

# Load environment variables from .env file
load_dotenv()

message_count = os.environ.get("MESSAGE_COUNT", 10)
delay_between_messages_seconds = os.environ.get(
    "DELAY_BETWEEN_MESSAGES_SECONDS", 3)
rabbitmq_connection_string = os.environ.get("RABBITMQ_CONNECTION_STRING", "")

print(f"MESSAGE_COUNT: {message_count}")
print(f"DELAY_BETWEEN_MESSAGES_SECONDS: {delay_between_messages_seconds}")
print(f"RABBITMQ_CONNECTION_STRING: {rabbitmq_connection_string}")

def send_messages():
    # Establish connection to RabbitMQ
    connection = pika.BlockingConnection(
        pika.URLParameters(rabbitmq_connection_string))
    channel = connection.channel()

    # Declare an exchange
    exchange_name = 'dapr-long-running-jobs-exchange'
    # Bind the queue to the exchange
    routing_key = 'job.run'

    try:
        for i in range(int(message_count)):
            message_id = str(uuid.uuid4())
            publish_time = time.time()

            message = json.dumps({
                "message_id": message_id,
                "message": f"Payload from Producer {i}",
                "publish_time": publish_time,
            })

            channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    message_id=message_id
                )
            )
            print(f" [x] Sent message: {message_id}")
            # Sleep for N seconds
            time.sleep(int(delay_between_messages_seconds))
    finally:
        connection.close()


if __name__ == '__main__':
    if not rabbitmq_connection_string:
        print("RABBITMQ_CONNECTION_STRING environment variable not set.")
        exit(1)

    send_messages()
