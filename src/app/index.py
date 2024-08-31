import json
import boto3
import logging
import starkbank
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError

# Configure logging
logging.basicConfig(level=logging.INFO)


def get_secrets(secret_names: list[str], region_name: str="us-west-2") -> dict[str, str | int]:
    """
    Retrieve secrets from AWS Secrets Manager.

    Args:
        secret_names (list): List of secret names to retrieve.
        region_name (str): AWS region where the secrets are stored.

    Returns:
        dict: A dictionary containing the retrieved secrets.

    Raises:
        ClientError: If a client error occurs during the secret retrieval.
        NoCredentialsError: If no AWS credentials are found.
        PartialCredentialsError: If incomplete AWS credentials are found.
        Exception: For any other unexpected errors.
    """
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    secrets = {}

    # Retrieve each secret by its name
    for secret_name in secret_names:
        try:
            # Attempt to retrieve the secret value
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
            secrets[secret_name] = get_secret_value_response["SecretString"]
        except (ClientError, NoCredentialsError, PartialCredentialsError) as e:
            logging.error(f"Failed to retrieve secret {secret_name}: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            raise

    return secrets


def _evaluate_amount(
    body_dict: dict[str, any]
) -> tuple[dict[str, any] | None, int | None]:
    # Extract the nominal amount from the invoice details in the body
    amount = body_dict.get("event", {}).get("log", {}).get("invoice", {}).get("amount")
    if amount is None:
        logging.error("amount not found in event body")
        return {
            "statusCode": 422,
            "body": json.dumps({"error": "amount not found in event body"}),
        }, None
    elif amount == 0:
        logging.error("amount cannot be 0")
        return {
            "statusCode": 422,
            "body": json.dumps({"error": "amount cannot be 0"}),
        }, 0
    return None, amount


def handler(event: dict[str, any], context=None) -> dict[str, str | int]:
    """
    AWS Lambda function handler to process incoming webhook requests.

    Args:
        event (dict): The event data, as an API Gateway request.
        context (LambdaContext): The runtime information of the Lambda function.
            Not part of the AWS SDK for Python (boto3).

    Returns:
        dict: The response object with status code and body.
    """

    # Define the secret names to retrieve
    secret_names = ["PRIVATE_KEY", "PROJECT_ID"]

    # Retrieve secrets from AWS Secrets Manager
    credentials = get_secrets(secret_names)

    # Initialize Stark Bank project
    project = starkbank.Project(
        environment="sandbox",  # Define the environment as 'sandbox'
        id=credentials["PROJECT_ID"],  # Use the project ID from the secrets
        private_key=credentials["PRIVATE_KEY"],  # Use the private key from the secrets
    )

    # Set the global user for Stark Bank operations
    starkbank.user = project

    try:
        # Extract the 'body' field from the event, which contains the JSON payload
        body_str = event.get("body")
        if not body_str:
            logging.error("No body found in the event")
            return {
                "statusCode": 422,
                "body": json.dumps({"error": "No body found in the event"}),
            }

        # Parse the JSON string into a dictionary
        body_dict = json.loads(body_str)
        logging.info(f"Received body: {body_dict}")

        error, amount = _evaluate_amount(body_dict)
        if error:
            return error

        # Create a transfer using Stark Bank SDK
        transfers = starkbank.transfer.create(
            [
                starkbank.Transfer(
                    amount=amount,
                    bank_code="20018183",  # Bank code for TED
                    branch_code="0001",  # Branch code
                    account_number="6341320293482496",  # Account number
                    account_type="payment",  # Account type
                    tax_id="20.018.183/0001-80",  # Tax ID of the recipient
                    name="Stark Bank S.A.",  # Recipient's name
                )
            ]
        )

        # Prepare the response body
        response_body = {
            "message": "Webhook received",
            "received_data": body_dict,
            "transfers_executed": [transfer.id for transfer in transfers],
        }

        # Return a successful response
        return {"statusCode": 200, "body": json.dumps(response_body)}

    except Exception as e:
        # Log any exceptions that occur during the handling of the event
        logging.error(f"An error occurred during the handling of the event: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
