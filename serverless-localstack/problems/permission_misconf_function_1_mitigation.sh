#!/bin/bash

set -e

ROLE_NAME="lambda-role"
POLICY_ARN="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
TRUST_POLICY='{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Service": "lambda.amazonaws.com"
    },
    "Action": "sts:AssumeRole"
  }]
}'

echo "🛠️  Checking if IAM role '$ROLE_NAME' exists..."

if awslocal iam get-role --role-name "$ROLE_NAME" > /dev/null 2>&1; then
  echo "⚠️  IAM role exists. Deleting it for a clean recovery..."
  awslocal iam delete-role --role-name "$ROLE_NAME"
  sleep 1
else
  echo "✅ No existing IAM role found. Proceeding with creation."
fi

echo "🚧 Creating IAM role '$ROLE_NAME'..."
awslocal iam create-role \
  --role-name "$ROLE_NAME" \
  --assume-role-policy-document "$TRUST_POLICY"

echo "🔗 Attaching AWSLambdaBasicExecutionRole policy..."
awslocal iam attach-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-arn "$POLICY_ARN"

echo "✅ IAM role '$ROLE_NAME' successfully recreated and configured."

# Optional: Show role info
echo "ℹ️  Current role configuration:"
awslocal iam get-role --role-name "$ROLE_NAME" | jq .