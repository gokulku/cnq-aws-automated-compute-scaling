import boto3
import json

ssm_client = boto3.client('ssm')
INSTANCE_ID = '<ENTER YOUR INSTANCE ID WHERE YOUR CNQ TERRAFORM IS RUNNING>' # Eg. i-xxxxxxxxxxxx
REGION = '<ENTER THE AWS REGION WHERE CNQ IS RUNNING>' # Eg. us-west-2
TERRAFORM_DIR = "<TERRAFORM DIRECTORY WHERE CNQ IS LOCATED WITHIN EC2>" # Eg. /home/ec2-user/aws-terraform-cnq-asg

def lambda_handler(event, context):
# ----------------------------------------------------------------------
    # Robustly extract the 'action' from the event payload.
    # This handles both direct invocation and the nested payload from Step Functions.
    # ----------------------------------------------------------------------
    # If using Step Functions, the actual payload is often found under 'Payload'
    input_payload = event.get('Payload', event) 
    action = input_payload.get('action')
    if not action:
        raise ValueError("Missing 'action' parameter in the invocation payload.")     
        return {
            'statusCode': 400,
            'body': json.dumps('Missing action parameter')
        } 
    if action == 'scale_out':
        # --- SCALE OUT ---
        commands = [
        f"cd {TERRAFORM_DIR}",
        # During scale out, specify your total desired node count for the "q_node_count" variable below. Eg. 3
        f"sed -i 's/^q_node_count[[:space:]]*=[[:space:]]*.*$/q_node_count = <ENTER THE DESIRED NODE COUNT>/' terraform.tfvars",
        "terraform init",
        "terraform apply -auto-approve"
   ]
      
    elif action == 'scale_in_p1':
        # --- SCALE DOWN PHASE 1  ---
        # During scale in, specify your total desired node count for the "q_target_node_count" variable below. Eg. 1
        commands = [
            f"cd {TERRAFORM_DIR}",
            f"sed -i 's/^q_target_node_count[[:space:]]*=[[:space:]]*.*$/q_target_node_count = <ENTER THE DESIRED NODE COUNT>/' terraform.tfvars",
            "terraform init",
            "terraform apply -auto-approve"
        ]

    elif action == 'scale_in_p2':
        # --- SCALE DOWN PHASE 2 ---
        # During scale in, specify your total desired node count for the "q_node_count" variable below. Eg. 1
        commands = [
            f"cd {TERRAFORM_DIR}",
            f"sed -i 's/^q_target_node_count[[:space:]]*=[[:space:]]*.*$/q_target_node_count = null/' terraform.tfvars",
            f"sed -i 's/^q_node_count[[:space:]]*=[[:space:]]*.*$/q_node_count = <ENTER THE DESIRED NODE COUNT>/' terraform.tfvars",
            "terraform init",
            "terraform apply -auto-approve"
        ]
        
    else:
        raise ValueError(f"Invalid action provided: {action}. Must be 'scale_out', 'scale_in_p1', or 'scale_in_p2'.")
        
    # --- Execute the SSM Run Command ---
    response = ssm_client.send_command(
        InstanceIds=[INSTANCE_ID],
        DocumentName='AWS-RunShellScript',
        Parameters={'commands': commands},
        TimeoutSeconds=3600
    )

    command_id = response['Command']['CommandId']
    
    # Return the command_id so the Step Function's WaitForSSMCompletion task can use it.
    return {
        'command_id': command_id,
        'action': action,
        'message': f"SSM Command {command_id} sent for action: {action}."
    }