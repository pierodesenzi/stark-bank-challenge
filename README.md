# Stark Bank Challenge: Lambda Webhook Handler with Stark Bank Integration
### by Piero Desenzi

This project is an AWS Lambda function designed to handle incoming webhook requests. It integrates with Stark Bank's API and utilizes AWS Secrets Manager for secure key management. The function processes the webhook events, performs financial transactions via Stark Bank, and returns appropriate responses based on the event data.

## Features

- **AWS Lambda Function**: Handles incoming HTTP POST requests through API Gateway.
- **Stark Bank Integration**: Processes financial transactions using Stark Bank's SDK.
- **AWS Secrets Manager**: Securely retrieves and manages secrets such as private keys and project IDs.
- **Error Handling**: Comprehensive error handling with logging for seamless debugging and monitoring.
- **Test Coverage**: Includes unit tests using `pytest` with `moto` for mocking AWS services.

## Project Structure

```bash
├── src
│   ├── template.yaml          # Unit tests for the handler function
│   └── function
│       └── index.py           # Lambda function code
├── tests
│   ├── __init__.py            # Initialization file
│   ├── test_requirements.txt  # Python dependencies for testing
│   └── test_index.py          # Unit tests for the handler function
├── Makefile                   # Build commands
├── README.md                  # Project documentation
└── requirements.txt           # Python dependencies
```

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/aws-lambda-webhook-starkbank.git
   cd aws-lambda-webhook-starkbank
   ```

2. **Install Python dependencies**:

   Make sure you have `pip` installed. Then, run:

   ```bash
   pip install -r requirements.txt
   ```

3. **Install additional test dependencies**:

   This project uses `pytest` and `moto` for testing:

   ```bash
   pip install pytest moto
   ```

## Usage

### 1. Environment Setup

Ensure that you have AWS CLI installed and that your AWS credentials are properly configured. This Lambda function relies on AWS Secrets Manager to store and retrieve sensitive information like `PRIVATE_KEY` and `PROJECT_ID`. Set these secrets in your AWS environment.

### 2. Running the Lambda Function Locally

To test the function locally, you can invoke it through the `pytest` tests provided. The function retrieves the necessary secrets, processes the event payload, and interacts with Stark Bank.

### 3. Deploying to AWS

You can deploy this Lambda function using AWS CloudFormation, AWS CLI, or other deployment tools like Serverless Framework. Make sure to configure your Lambda function's environment variables and IAM roles properly.

### 4. Running Tests

To run the tests:

```bash
pytest tests/
```

The tests include:

- **`test_get_secrets`**: Ensures that secrets are correctly retrieved from AWS Secrets Manager.
- **`test_handler_success`**: Tests a successful webhook event processing.
- **`test_handler_no_body`**: Tests the handler's response when no body is present in the event.
- **`test_handler_nominalAmount_zero`**: Tests the response when the nominal amount is zero.
- **`test_handler_missing_nominalAmount`**: Tests the response when the nominal amount is missing.

### 5. Building and Packaging

To create a deployment package, including the Lambda function code and its dependencies, use the Makefile provided:

```bash
make zip
```

This will create a `.zip` file containing your Lambda function ready for deployment.

## Configuration

### Changing Lambda Timeout

- makefile vars
- template.yaml