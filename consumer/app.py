import logging
from dapr.ext.grpc import App
from instance_id import InstanceID
from rabbitmq_consumer import RabbitMQConsumer
import asyncio
from workflows.long_running_workflow import workflow_runtime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the instance ID from the environment
instance_id = InstanceID().id
app_port = os.environ.get("APP_PORT", 6000)

app = App()
pubsub_name='local-rabbitmq'
exchange_name='long_running_jobs_exchange'
metadata={"queueName": "long_running_jobs_queue", "routingKey": "job.run"}

async def main():
    logger.info(f"Starting app instance {instance_id}...")
    consumer = RabbitMQConsumer(app,pubsub_name,exchange_name,metadata,app_port) 
    await asyncio.gather(
        consumer.run(),
        workflow_runtime.start()
    )

if __name__ == '__main__':         
    asyncio.run(main())