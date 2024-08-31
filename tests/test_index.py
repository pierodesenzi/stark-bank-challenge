import json
import boto3
import pytest
import moto
import os
from src.function.index import get_secrets, handler


# Sample event for testing
@pytest.fixture
def api_gateway_event():
    return {
        "body": json.dumps(
            {
                "event": {
                    "log": {
                        "invoice": {
                            "amount": 1  # Set a amount for testing
                        }
                    }
                }
            }
        )
    }


@pytest.fixture
def api_gateway_event_amount_zero():
    return {
        "body": json.dumps(
            {
                "event": {
                    "log": {
                        "invoice": {
                            "amount": 0  # Test case for zero amount
                        }
                    }
                }
            }
        )
    }


@pytest.fixture
def api_gateway_event_no_amount():
    return {
        "body": json.dumps(
            {
                "event": {
                    "log": {
                        "invoice": {
                            # Missing amount field for testing error handling
                        }
                    }
                }
            }
        )
    }


# Fixture for mocking AWS Secrets Manager
@pytest.fixture(scope="session")
def mock_secrets_manager():
    with moto.mock_aws():
        session = boto3.Session(
            aws_access_key_id="ABCDE",
            aws_secret_access_key="KLMNO",
            region_name="us-west-2",  # Mocked region for testing
        )
        secrets_client = boto3.client("secretsmanager", region_name="us-west-2")
        # Creating mock secrets with environment variables
        secrets_client.create_secret(
            Name="PRIVATE_KEY", SecretString=os.getenv("PRIVATE_KEY")
        )
        secrets_client.create_secret(
            Name="PROJECT_ID", SecretString=os.getenv("PROJECT_ID")
        )
        yield session


# Test the get_secrets function with mocked Secrets Manager
def test_get_secrets(mock_secrets_manager):
    secret_names = ["PRIVATE_KEY", "PROJECT_ID"]
    secrets = get_secrets(secret_names)

    # Assertions to verify secrets are retrieved correctly
    assert secrets["PRIVATE_KEY"] == os.getenv("PRIVATE_KEY")
    assert secrets["PROJECT_ID"] == os.getenv("PROJECT_ID")


# Test handler function for successful execution
def test_handler_success(api_gateway_event, mock_secrets_manager):
    response = handler(api_gateway_event, None)

    assert response["statusCode"] == 200  # Ensure success status code
    body = json.loads(response["body"])
    assert body["message"] == "Webhook received"
    assert body["received_data"] == json.loads(api_gateway_event["body"])


# Test handler function when no body is provided in the event
def test_handler_no_body(api_gateway_event, mock_secrets_manager):
    api_gateway_event["body"] = None  # Simulate missing body

    response = handler(api_gateway_event, None)

    assert response["statusCode"] == 422  # Ensure error status code
    body = json.loads(response["body"])
    assert body["error"] == "No body found in the event"


# Test handler function when amount is zero
def test_handler_amount_zero(
    api_gateway_event_amount_zero, mock_secrets_manager
):
    response = handler(api_gateway_event_amount_zero, None)

    assert response["statusCode"] == 422  # Ensure error status code
    body = json.loads(response["body"])
    assert body["error"] == "amount cannot be 0"


# Test handler function when amount is missing
def test_handler_missing_amount(
    api_gateway_event_no_amount, mock_secrets_manager
):
    response = handler(api_gateway_event_no_amount, None)

    assert response["statusCode"] == 422  # Ensure error status code
    body = json.loads(response["body"])
    assert body["error"] == "amount not found in event body"
