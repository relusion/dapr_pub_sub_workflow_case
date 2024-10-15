from cloudevents.sdk.event import v1
from dapr.ext.grpc import App
from dapr.clients import DaprClient
import logging
import datetime
import json
import os
from instance_id import InstanceID

logger = logging.getLogger(__name__)

class RabbitMQConsumer:
    def __init__(self, app: App, pubsub_name: str, exchange_name: str, metadata: dict, port: int = 6000):
        self.app = app
        self.pubsub_name = pubsub_name
        self.exchange_name = exchange_name
        self.metadata = metadata
        self.port = port
        self.setup_subscription()

    def setup_subscription(self):
        instance_id = InstanceID().id
        logger.info(f"{instance_id}: Setting up subscription for exchange: {self.exchange_name}")

        @self.app.subscribe(pubsub_name=self.pubsub_name, topic=self.exchange_name, metadata=self.metadata)
        def message_handler(event: dict) -> None:
            start_time = datetime.datetime.now()
            instance_id = InstanceID().id
            receive_time = start_time.isoformat()
            message = event.extensions
            logger.info(f"Received message: {message} at {receive_time}")
            message_id = message["message_id"]
            # add receive time to the message
            message["receive_time"] = receive_time
            logger.info(f"Received message: {message_id} at {receive_time}")

            # Start the workflow
            with DaprClient() as client:
                workflow_response = client.start_workflow(
                    workflow_component="dapr",
                    workflow_name="long_running_workflow",
                    input=message,
                    # workflow_options=workflow_options,
                )
                instance_id = workflow_response.instance_id

                correlation = {
                    "message_id": message_id,
                    "workflow_instance_id": instance_id,
                    "receive_time": receive_time,
                    # "original_timestamp": message["timestamp"]
                }
                logger.info(f"Correlation: {json.dumps(correlation)}")                

    async def run(self):
        await self.app.run(self.port)
