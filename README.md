# Stark Bank Challenge: Lambda Webhook Handler with Stark Bank Integration
### by Piero Desenzi

This project is an AWS project based around a Lambda function designed to handle incoming webhook requests from Stark Bank. It integrates with the bank's API and utilizes AWS Secrets Manager for secure key management. The function processes the webhook events, performs financial transactions via Stark Bank's API, and returns appropriate responses based on the event data.

The objective of the Lambda function is to receive a webhook call from Stark Bank via AWS API Gateway describing a new Invoice received, and then take the received amout and transer it to a determined Stark Bank account.

## Features

- **AWS Lambda Function**: Handles incoming HTTP POST requests through API Gateway.
- **Stark Bank Integration**: Processes financial transactions using Stark Bank's SDK.
- **Error Handling**: Comprehensive error handling with logging for seamless debugging and monitoring.
- **Test Coverage**: Includes unit tests using `pytest` with `moto` for mocking AWS services.
- **One-line deploy**: The full deployment process on AWS is taken care of using Makefile.

## Project Structure

```bash
├── src
│   ├── template.yaml              # template for AWS CloudFormation
│   └── function
│       ├── local_invoker.py       # Script to call the Lambda function locally
│       ├── periodic_issuer.py     # Script to issue periodic invoices
│       ├── index.py               # Code to be deployed on AWS Lambda
│       └── local_requirements.txt # Python dependencies for local execution
├── tests
│   ├── __init__.py                # Initialization file
│   ├── test_requirements.txt      # Python dependencies for testing
│   └── test_index.py              # Unit tests for index.py
├── Makefile                       # Build commands
├── README.md                      # Project documentation
└── requirements.txt               # Python dependencies
```

## Installation

#### 1. Clone the repository:

   ```bash
   git clone https://github.com/pierodesenzi/stark-bank-challenge
   cd stark-bank-challenge
   ```

#### 2. Install AWS CLI:

   Follow the [official installation guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) for your operating system.

#### 3. Configure AWS CLI:

   After installation, configure the CLI with your credentials:

   ```bash
   aws configure
   ```

   You'll be prompted to enter your AWS Access Key ID, Secret Access Key, region, and output format. Example:

   ```
   AWS Access Key ID [None]: YOUR_ACCESS_KEY_ID
   AWS Secret Access Key [None]: YOUR_SECRET_ACCESS_KEY
   Default region name [None]: us-west-2
   Default output format [None]: json
   ```

#### 4. Verify the Configuration:

   To verify that the AWS CLI is set up correctly, run:

   ```bash
   aws sts get-caller-identity
   ```

   This command should return details about your IAM identity.

#### 5. Environment Setup:

- Ensure that your AWS credentials are properly configured. This Lambda function relies on AWS Secrets Manager to store and retrieve sensitive information like `PRIVATE_KEY` and `PROJECT_ID`. Set these secrets in your AWS environment.
- Create a role with permissions to S3, Secrets Manager, Lambda and CloudFormation, either via AWS CLI or the AWS web page.
- Replace the values in templates.yaml, under `Parameters`, with the actual values of your AWS `client_id` and IAM Role name.


## Usage

#### 1. Running Locally Simulating a Webhook Call

First of all, install the base dependencies.

```bash
pip install -r requirements.txt
```

To simulate locally a webhook call, you can run the file `src/function/local_invoker.py`. This script invokes the function `handler(event, context=None)` in `index.py` with a dict as the first parameter, shaped like the following:

```python
{"body": '{"event": {"log": {"invoice": {"amount": 100}}}}'}
```

The function `handler` is meant to do a transaction worth the same amount to a Stark Bank account, so further information is not needed on `body`.

#### 2. Deployment to AWS

To deploy the project on AWS using CloudFormation:

```bash
make deploy
```

In order for the webhook to be called when a new invoice is created, go to Stark Bank's Sandbox, create a Webhook, and add the API Gateway link for the `/webhook` endpoint in the URL field. The link should look like this:
```
https://ucza2pi6t6.execute-api.us-west-2.amazonaws.com/prod/webhook
```
Then add `invoice` to the `Subscriptions` field.

#### 3. Periodically creating invoices

If you need to create invoices for the Stark Bank account on Sandbox, you can pip install `local_requirements.txt` in `src/function` and then run:
```bash
python src/function/periodic_issuer.py
```

This script issues 8 to 12 Invoices every 3 hours to random people for 24 hours. These invoices will trigger the Lambda function deployed on AWS.

#### 3. Bring down deployment

To tear down a Stack created with AWS CloudFormation (considering the name of the Stack was not changed in Makefile since the deployment):

```bash
make tear-down
```

If the Stack is stuck in DELETE_FAILED:

```bash
make force-tear-down
```

#### 4. Running Tests

To run the tests locally, you need authentication variables to connect to Stark Bank, since these tests involve API calls. For such, you need to have PRIVATE_KEY and PROJECT_ID set as environment variables locally.

To install all packages (base and testing) and run the tests:

```bash
make test
```

To only run the tests, if you already have the test dependencies installed:

```bash
pytest -vvs .
```

The tests include:

- **`test_get_secrets`**: Ensures that secrets are correctly retrieved from AWS Secrets Manager.
- **`test_handler_success`**: Tests a successful webhook event processing, creating a new transaction.
- **`test_handler_no_body`**: Tests the handler's response when no body is present in the event.
- **`test_handler_amount_zero`**: Tests the response when the nominal amount is zero.
- **`test_handler_missing_amount`**: Tests the response when the nominal amount is missing.


## Configuration

In `Makefile`, the following parameters can be changed:

- **`REQUIREMENTS_FILE`**:
  Path to the `requirements.txt` file, which contains the Python dependencies for your Lambda function.

- **`ZIP_FILE`**:
  The name of the ephemeral zip file that will be created, containing the Lambda function code and dependencies.

- **`S3_BUCKET`**:
  The name of the S3 bucket where the zip file will be uploaded.

- **`S3_ZIP_PATH`**:
  The path within the S3 bucket where the zip file will be stored.

- **`TEMPLATE_FILE`**:
  The name of the CloudFormation template file (`template.yaml`) used to deploy the AWS resources.

- **`STACK_NAME`**:
  The name of the CloudFormation stack that will be created or updated.

- **`TEST_REQUIREMENTS_FILE`**:
  Path to the `test_requirements.txt` file, which contains the Python dependencies needed for testing.

- **`TEMP_DIR`**:
  The temporary directory used during the build process for storing intermediate files.


In `template.yaml`, the following parameters can be changed:

- **`ClientId`**:
  AWS account ID that owns the IAM role. This is used to construct the ARN for the Lambda execution role.

- **`RoleName`**:
  Name of the IAM role that the Lambda function will use to execute. This role must have the necessary permissions to access the resources: S3, Secrets Manager, Lambda, and CloudFormation.

- **`Timeout`**:
  The amount of time that the Lambda function is allowed to run before it is terminated. This is specified in seconds.

- **`ApiGateway.Properties.Name`**:
  The name of the API Gateway that will be created for the Lambda function. This name will be visible in the AWS API Gateway console.
