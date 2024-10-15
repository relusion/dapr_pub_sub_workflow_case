# Dapr Pub-Sub Workflow Case

This repository demonstrates an issue where workflows are scheduled but not executed due to Dapr sidecar errors.

## Problem Overview

- **Expected Behavior**: Workflows should be scheduled, retried on failure, and eventually completed when resources are available.
- **Actual Behavior**: Workflows are scheduled but not executed, with the following error logged repeatedly:

  ```
  "timed-out trying to schedule a workflow execution - this can happen if there are too many in-flight workflows or if the workflow engine isn't running: context deadline exceeded"
  ```

## Steps to Reproduce

1. **Clone the repo**:
   ```bash
   git clone https://github.com/relusion/dapr_pub_sub_workflow_case.git
   cd dapr_pub_sub_workflow_case
   ```
2. **Start environment**:
   ```bash
   docker-compose up --build
   ```
3. **Generate messages**:
   - Run the producer to send 100 messages:
   ```bash
   cd producer
   python producer.py
   ```
4. **Observe**:  
   - The consumer app schedules workflows, but they aren't executed. Check Dapr logs for timeout errors.



