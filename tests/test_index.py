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
        "body": json.dumps({
            "event": {
                "log": {
                    "invoice": {
                        "nominalAmount": 1
                    }
                }
            }
        })
    }

@pytest.fixture
def api_gateway_event_amount_zero():
    return {
        "body": json.dumps({
            "event": {
                "log": {
                    "invoice": {
                        "nominalAmount": 0
                    }
                }
            }
        })
    }

@pytest.fixture
def api_gateway_event_no_amount():
    return {
        "body": json.dumps({
            "event": {
                "log": {
                    "invoice": {
                    }
                }
            }
        })
    }


@pytest.fixture(scope="session")
def mock_secrets_manager():
    with moto.mock_aws():
        session = boto3.Session(
            aws_access_key_id="ABCDE",
            aws_secret_access_key="KLMNO",
            region_name="us-west-2"
        )
        secrets_client = boto3.client("secretsmanager", region_name="us-west-2")
        secrets_client.create_secret(Name="PRIVATE_KEY", SecretString=os.getenv('PRIVATE_KEY'))
        secrets_client.create_secret(Name="PROJECT_ID", SecretString=os.getenv('PROJECT_ID'))
        yield session

def test_get_secrets(mock_secrets_manager):
    secret_names = ["PRIVATE_KEY", "PROJECT_ID"]
    secrets = get_secrets(secret_names)
    
    assert secrets["PRIVATE_KEY"] == os.getenv('PRIVATE_KEY')
    assert secrets["PROJECT_ID"] == os.getenv('PROJECT_ID')


def test_handler_success(api_gateway_event, mock_secrets_manager):

    response = handler(api_gateway_event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["message"] == "Webhook received"
    assert body["received_data"] == json.loads(api_gateway_event["body"])


def test_handler_no_body(api_gateway_event, mock_secrets_manager):
    api_gateway_event["body"] = None

    response = handler(api_gateway_event, None)

    assert response["statusCode"] == 422
    body = json.loads(response["body"])
    assert body["error"] == "No body found in the event"

def test_handler_nominalAmount_zero(api_gateway_event_amount_zero, mock_secrets_manager):
    response = handler(api_gateway_event_amount_zero, None)

    assert response["statusCode"] == 422
    body = json.loads(response["body"])
    assert body["error"] == "nominalAmount cannot be 0"

def test_handler_missing_nominalAmount(api_gateway_event_no_amount, mock_secrets_manager):
    response = handler(api_gateway_event_no_amount, None)

    assert response["statusCode"] == 422
    body = json.loads(response["body"])
    assert body["error"] == "nominalAmount not found in event body"