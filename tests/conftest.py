# test/conftest.py
from distutils.util import strtobool
import json
import os
import urllib

import boto3
import pytest
import vcr
from dotenv import load_dotenv
from moto import mock_s3

from dspace.client import DSpaceClient

load_dotenv()


@pytest.fixture(scope="function")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(scope="function")
def mocked_s3(aws_credentials):
    with mock_s3():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-bucket")
        s3.put_object(
            Bucket="test-bucket",
            Key="path/file/test-file-03.txt",
            Body="Test content",
        )
        yield s3


@pytest.fixture
def my_vcr():
    my_vcr = vcr.VCR(
        before_record_request=vcr_scrub_request,
        before_record_response=vcr_scrub_response,
        decode_compressed_response=True,
        filter_post_data_parameters=[
            ("email", "user@example.com"),
            ("password", "password"),
        ],
        filter_headers=[("Cookie", "JSESSIONID=sessioncookie")],
    )
    return my_vcr


@pytest.fixture
def test_client(my_vcr, vcr_env):
    #with my_vcr.use_cassette("tests/vcr_cassettes/client/login.yaml"):
    client = DSpaceClient(vcr_env["url"], verify=vcr_env["verify"])
    client.login(vcr_env["email"], vcr_env["password"])
    return client


@pytest.fixture
def test_file_path_01():
    return os.path.abspath("tests/fixtures/test-file-01.pdf")


@pytest.fixture
def test_file_path_02():
    return os.path.abspath("tests/fixtures/test-file-02.txt")


@pytest.fixture
def vcr_env():
    if os.getenv("DSPACE_PYTHON_CLIENT_ENV") == "vcr_create_cassettes":
        env = {
            "url": os.environ["TEST_DSPACE_API_URL"],
            "email": os.environ["TEST_DSPACE_EMAIL"],
            "password": os.environ["TEST_DSPACE_PASSWORD"],
            "verify": bool(strtobool(os.getenv("TEST_DSPACE_SSL_VERIFY", "True"))),
            "test_collection_handle": os.getenv("TEST_DSPACE_COLLECTION_HANDLE", "1721.1/130884"),
            "test_collection_uuid": os.getenv("TEST_DSPACE_COLLECTION_UUID", "72dfcada-de27-4ce7-99cc-68266ebfd00c"),
            "test_collection_name": os.getenv("TEST_DSPACE_COLLECTION_NAME", "Graduate Theses"),
            "test_collection_type": os.getenv("TEST_DSPACE_COLLECTION_TYPE", "collection"),
        }
    else:
        env = {
            "url": "https://dspace-example.com/rest",
            "email": "user@example.com",
            "password": "password",
            "verify": True,
            "test_collection_handle": "1721.1/130884",
            "test_collection_uuid": "72dfcada-de27-4ce7-99cc-68266ebfd00c",
            "test_collection_name": "Graduate Theses",
            "test_collection_type": "collection",
        }
    return env


def vcr_scrub_request(request):
    """Replaces the request URI with fake data"""
    split_uri = urllib.parse.urlsplit(request.uri)
    new_uri = urllib.parse.urljoin("https://dspace-example.com", split_uri.path)
    request.uri = new_uri
    return request


def vcr_scrub_response(response):
    """Replaces the response session cookie and any user data in the response body with
    fake data. Also replaces response body content that isn't needed for testing."""
    if "Set-Cookie" in response["headers"]:
        response["headers"]["Set-Cookie"] = [
            "JSESSIONID=sessioncookie; Path=/rest; Secure; HttpOnly"
        ]
    try:
        response_json = json.loads(response["body"]["string"])
    except json.decoder.JSONDecodeError:
        pass
    else:
        response_json.pop("introductoryText", None)
        try:
            email = response_json["email"]
            if email is not None:
                response_json["email"] = "user@example.com"
                response_json["fullname"] = "Test User"
        except (KeyError, TypeError):
            pass
        if response_json != json.loads(response["body"]["string"]):
            response["body"]["string"] = json.dumps(response_json)
    return response
