import os
import zipfile
import boto3
import json
from pathlib import Path
from botocore.exceptions import ClientError

os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

lambda_client = boto3.client("lambda", endpoint_url="http://localhost:4566")
iam_client = boto3.client("iam", endpoint_url="http://localhost:4566")

ROLE_NAME = "lambda-role"
ROLE_ARN = f"arn:aws:iam::000000000000:role/{ROLE_NAME}"

def check_role_exists(role_name):
    try:
        iam_client.get_role(RoleName=role_name)
        return True
    except iam_client.exceptions.NoSuchEntityException:
        print(f"[ERROR] IAM role '{role_name}' not found.")
        return False
    except ClientError as e:
        print(f"[ERROR] Failed to verify role: {e}")
        return False

def create_zip(zip_name, source_file):
    with zipfile.ZipFile(zip_name, "w") as z:
        z.write(source_file, arcname="lambda_function.py")

def deploy_lambda(name, source):
    if not check_role_exists(ROLE_NAME):
        print(f"[SKIP] Skipping deployment of '{name}' due to missing IAM role.")
        return

    zip_path = f"{name}.zip"
    create_zip(zip_path, source)

    try:
        with open(zip_path, "rb") as f:
            lambda_client.create_function(
                FunctionName=name,
                Runtime="python3.9",
                Role=ROLE_ARN,
                Handler="lambda_function.handler",
                Code={"ZipFile": f.read()},
                Publish=True,
            )
        print(f"[LOG] Successfully deployed {name} from {source}")
    except ClientError as e:
        print(f"[ERROR] Failed to deploy {name}: {e.response['Error']['Message']}")

if __name__ == '__main__':
    deploy_lambda("test_function_1", "lambda_functions/test_function_1.py")
    deploy_lambda("test_function_2", "lambda_functions/test_function_2.py")
