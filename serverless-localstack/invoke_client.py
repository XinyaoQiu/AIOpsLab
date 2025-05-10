import boto3
import json
import os

os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

lambda_client = boto3.client("lambda", endpoint_url="http://localhost:4566")

def invoke_function(function_name, payload=None) -> bool:
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload or {})
        )
        print(f"{function_name} =>", response['Payload'].read().decode())
        return True
    except Exception as e:
        print(f"{function_name} FAILED:", str(e))
        return False

if __name__ == '__main__':
    invoke_function("test_function_1", {"name": "Alice", "delay": 2, "load": 12})
    invoke_function("test_function_2", {"user": "error", "delay": 1})  # should raise error
