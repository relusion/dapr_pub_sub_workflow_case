#!/bin/sh

# Wait for RabbitMQ to start
sleep 10

# Create exchanges
rabbitmqadmin declare exchange name=dapr-long-running-jobs-exchange type=fanout
rabbitmqadmin declare exchange name=system-logs-exchange type=fanout
rabbitmqadmin declare exchange name=user-notifications-exchange type=fanout

# Create queues with dead-letter configuration
rabbitmqadmin declare queue name=long_running_jobs_queue durable=true     arguments='{"x-dead-letter-exchange": "dlx-long_running_jobs_queue"}'
rabbitmqadmin declare queue name=dlx-long_running_jobs_queue durable=true
rabbitmqadmin declare queue name=system_logs_queue durable=true
rabbitmqadmin declare queue name=user_notifications_queue durable=true

# Bind queues to their respective exchanges
rabbitmqadmin declare binding source=dapr-long-running-jobs-exchange destination_type=queue destination=long_running_jobs_queue routing_key=job.run
rabbitmqadmin declare binding source=system-logs-exchange destination_type=queue destination=system_logs_queue routing_key=system.log
rabbitmqadmin declare binding source=user-notifications-exchange destination_type=queue destination=user_notifications_queue routing_key=user.notify

echo "RabbitMQ configuration with Dead Letter Exchange setup completed."
