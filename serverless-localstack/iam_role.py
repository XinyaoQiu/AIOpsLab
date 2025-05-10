import boto3
import os
import json
from botocore.exceptions import ClientError

os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

iam_client = boto3.client("iam", endpoint_url="http://localhost:4566")

ROLE_NAME = "lambda-role"
ROLE_ARN = f"arn:aws:iam::000000000000:role/{ROLE_NAME}"
POLICY_ARN = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"

assume_role_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {
            "Service": "lambda.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
    }]
}

def recover_iam_role():
    try:
        iam_client.get_role(RoleName=ROLE_NAME)
        print(f"[INFO] IAM role '{ROLE_NAME}' already exists.")
        return
    except iam_client.exceptions.NoSuchEntityException:
        print(f"[INFO] IAM role '{ROLE_NAME}' not found. Creating...")

    try:
        iam_client.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy)
        )
        print(f"[LOG] Created role '{ROLE_NAME}'.")

        iam_client.attach_role_policy(
            RoleName=ROLE_NAME,
            PolicyArn=POLICY_ARN
        )
        print(f"[LOG] Attached basic execution policy to '{ROLE_NAME}'.")
    except ClientError as e:
        print(f"[ERROR] Failed to create or configure IAM role: {e.response['Error']['Message']}")

if __name__ == "__main__":
    recover_iam_role()
