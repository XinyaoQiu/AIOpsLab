import boto3
import os
import json
import time

os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

iam_client = boto3.client("iam", endpoint_url="http://localhost:4566")
lambda_client = boto3.client("lambda", endpoint_url="http://localhost:4566")

_ROLE_NAME = "lambda-role"
_ROLE_ARN = f"arn:aws:iam::000000000000:role/{_ROLE_NAME}"

def _inject():
    """
    Simulates an infrastructure-level fault by deleting the IAM execution role,
    making Lambda invocations/deployments fail due to missing role.
    """
    for i in range(10):
        try:
            # Detach and delete role to simulate misconfiguration
            print(f"Injecting fault: Deleting IAM role {_ROLE_NAME}")
            policies = iam_client.list_attached_role_policies(RoleName=_ROLE_NAME)
            for p in policies.get("AttachedPolicies", []):
                iam_client.detach_role_policy(
                    RoleName=_ROLE_NAME,
                    PolicyArn=p["PolicyArn"]
                )
            iam_client.delete_role(RoleName=_ROLE_NAME)
            print("Fault injected: IAM role deleted.")
            return
        except Exception as e:
            print(f"Failed to inject fault: {e}")
            time.sleep(5)
    raise Exception("Fault injection timeout!")

def _recover():
    """
    Recreates the IAM role needed for Lambda to function correctly.
    """
    assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }

    try:
        print(f"Recovering: Recreating IAM role {_ROLE_NAME}")
        iam_client.create_role(
            RoleName=_ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy)
        )
        iam_client.attach_role_policy(
            RoleName=_ROLE_NAME,
            PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        )
        print("Recovery successful: IAM role recreated.")
    except Exception as e:
        print(f"Recovery failed: {e}")
