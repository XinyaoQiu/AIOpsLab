import boto3
import os

os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

lambda_client = boto3.client("lambda", endpoint_url="http://localhost:4566")

def delete_lambda(function_name):
    try:
        lambda_client.delete_function(FunctionName=function_name)
        print(f"Deleted: {function_name}")
    except Exception as e:
        print(f"Failed to delete {function_name}: {e}")

if __name__ == '__main__':
    delete_lambda("test_function_1")
    delete_lambda("test_function_2")
