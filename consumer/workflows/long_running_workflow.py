from dapr.clients import DaprClient
from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowContext,WorkflowActivityContext
import time
import json
import logging
import os
from instance_id import InstanceID

logger = logging.getLogger(__name__)

# Get the instance ID from the environment
instance_id = InstanceID().id

def long_running_workflow(context: DaprWorkflowContext, wf_input):
    # This is the main workflow function
    # Entering here means the workflow has been triggered, and it will enter here before calling any activities, because of the yield keyword
    logger.info(f"{instance_id}: Entering long_running_workflow with input: {wf_input}")    
    
    try:                
        status = yield context.call_activity(log_workflow_start,input=wf_input)
        result = yield context.call_activity(process_data,input=status) 
        result = yield context.call_activity(process_data_ex,input=result)         
        yield context.call_activity(notify_results,input=result)
        yield context.call_activity(log_workflow_complete,input=result)           
    except Exception as e:
        logger.error(f"Instance: {instance_id}, workflow:{context.instance_id}: Workflow failed with error: {e}")
        yield context.call_activity(error_handler, input=str(e))        
        raise
    finally:
        logger.info(f"Instance: {instance_id}, workflow:{context.instance_id}: Workflow completed")
    return [result]

def log_workflow_complete(ctx: WorkflowActivityContext, wf_input):
    message_id = wf_input.get('message_id')
    publish_time = wf_input.get('publish_time')
    current_time = time.time()
    processing_time = current_time - publish_time

    # Create a dictionary of custom properties
    custom_properties = {
        "custom.message_id": message_id,
        "custom.operation": "process_workflow",
        "custom.processing_time_sec": str(processing_time)  # Convert to string as properties are typically strings
    }
    
    logger.info(f"Instance: {instance_id}, workflow:{ctx.workflow_id}: Executing log_workflow_complete with input: {wf_input}")
    return wf_input

def log_workflow_start(ctx: WorkflowActivityContext, wf_input):    
    logger.info(f"Instance: {instance_id}, workflow:{ctx.workflow_id}: Executing log_workflow_start with input: {wf_input}")
    return wf_input

def process_data(ctx: WorkflowActivityContext, wf_input):
    logger.info(f"Instance: {instance_id}, workflow:{ctx.workflow_id}: Initiating process_data with input: {wf_input}")    
    for i in range(3):
        logger.info(f"{instance_id}: Processing step {i+1}/3...")
        time.sleep(10)  # Simulate processing time for each step
    logger.info(f"{instance_id}: Data processing dance complete!")
    # add fake property to the result
    wf_input["process_data"] = f"Transformed {wf_input}"    
    return wf_input

def process_data_ex(ctx: WorkflowActivityContext, wf_input):
    logger.info(f"{instance_id}: Executing process_data_ex with input: {wf_input}")    
    for i in range(5):
        logger.info(f"{instance_id}: Transformation phase {i+1}/5: Enhancing data quality...")
        time.sleep(6)  # Simulate processing time for each phase
    logger.info(f"{instance_id}: Advanced data transformation complete!")
    wf_input["process_data_ex"] = f"Transformed {wf_input}"    
    return wf_input

def notify_results(ctx: WorkflowActivityContext, wf_input):
    logger.info(f"{instance_id}: Executing notify_results with input: {wf_input}")    
    result_event = {
        "app_instance_id": instance_id,
        "workflow_instance_id": ctx.workflow_id,
        "message": "Data processing complete!",
        "data": wf_input,
        "timestamp": time.time()
    }
    json_str = json.dumps(result_event)
    # Send a message using Dapr pub/sub
    with DaprClient() as client:
        client.publish_event(
            pubsub_name="local-rabbitmq",
            topic_name="user-notifications-exchange",
            data=json_str,
            data_content_type="application/json",
            publish_metadata={
                "queueName": "user_notifications_queue",
                "routingKey": "user.notify"
            }
        )
        print(f"Sent processed data: {wf_input}")
        
    return wf_input
        
def error_handler(ctx, error):
    logger.info(f"{instance_id}: Executing error_handler with input: {error}")    
    json_str = json.dumps(error)
    with DaprClient() as client:
        client.publish_event(
            pubsub_name="local-rabbitmq",
            topic_name="system-logs-exchange",
            data=json_str,
            data_content_type="application/json",
            publish_metadata={
                "queueName": "user_notifications_queue",
                "routingKey": "system.log"
            }
        )            

workflow_runtime = WorkflowRuntime()
workflow_runtime.register_workflow(long_running_workflow)
workflow_runtime.register_activity(log_workflow_start)
workflow_runtime.register_activity(log_workflow_complete)
workflow_runtime.register_activity(process_data)
workflow_runtime.register_activity(process_data_ex)
workflow_runtime.register_activity(notify_results)
workflow_runtime.register_activity(error_handler)

