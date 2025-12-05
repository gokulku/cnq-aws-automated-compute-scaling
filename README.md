# CNQ AWS Automated Compute Scaling

## Overview

This project enables scheduled scaling (add/remove EC2 nodes) for a Qumulo cloud-native (CNQ) cluster running on AWS. Scaling is triggered by a schedule using EventBridge Scheduler, orchestrated with Step Functions, and executed via Lambda + SSM + Terraform.

## Repository Structure


├── lambda_source/ # AWS Lambda code: edits tf.vars and runs Terraform via SSM

├── step_functions/ # State machine definitions for scale-out / scale-in workflows

├── images/ # Diagrams or visuals 

├── README.md # This documentation

├── LICENSE # MIT license

└── .gitignore


## Prerequisites

- AWS account with permissions to manage IAM, EC2, SSM, Lambda, Step Functions, EventBridge Scheduler, and any other AWS resources your Terraform code uses.  
- Existing Terraform for your Cloud Native Qumulo running on an EC2 node, along with a `tf.vars` file controlling scaling parameters.  
- AWS credentials configured (CLI, console, or SDK) for deployment.  

## Deployment & Setup Steps

1. Deploy Lambda and Step Functions:
   - Create a Lambda function using code from `lambda_source/`.  
   - Create two Step Function state machines (one each for scale out and scale in) using definitions from `step_functions/`.  
   - Assign appropriate IAM roles/policies to Lambda & Step Functions.  

2. Configure IAM Roles & Policies (least-privilege):
   - Lambda role: permissions for SSM (`SendCommand`, etc.), Terraform resource operations, S3 (if needed), EC2 operations, etc.  
   - Step Functions role: `lambda:InvokeFunction`.  
   - EventBridge Scheduler role: `states:StartExecution` on Step Functions ARN.  

3. Create scheduled scaling events:
   - Use EventBridge Scheduler to trigger Step Functions per schedule (cron or rate).  
   - Optionally set retry policy, DLQ, time windows.  

4. Test:
   - Trigger workflow via Eventbridge/lambda directly to validate.  
   - Verify EC2 nodes are added or removed correctly.  
   - Check CloudWatch logs and Terraform output.  

5. Enable schedule and monitor:
   - Monitor first few runs carefully.  
   - Use tagging, logging, and alerts for visibility.  

