# tests/test_client.py

import pytest
import requests

from dspace.bitstream import Bitstream
from dspace.client import DSpaceClient
from dspace.item import Item, MetadataEntry


def test_client_instantiates_with_expected_values():
    client = DSpaceClient("https://dspace-example.com/rest")
    assert client.headers["accept"] == "application/json"
    assert client.base_url == "https://dspace-example.com/rest"
    assert client.timeout == 3.0


def test_client_repr():
    client = DSpaceClient("https://dspace-example.com/rest")
    assert str(client) == (
        "DSpaceClient(base_url='https://dspace-example.com/rest', "
        "accept_header='application/json', "
        "timeout=3.0)"
    )


def test_client_delete_method(my_vcr, test_client, vcr_env, test_file_path_01):
    with my_vcr.use_cassette("tests/vcr_cassettes/client/delete_bitstream.yaml"):
        bitstream = Bitstream(
            name="test-file-01.pdf",
            description="A test PDF file",
            file_path=test_file_path_01,
        )
        item = Item(
            metadata=[
                MetadataEntry(key="dc.title", value="Test Item for Bitstream"),
                MetadataEntry(key="dc.contributor.author", value="Jane Doe. Author"),
            ]
        )
        item.post(test_client, collection_handle=vcr_env["test_collection_handle"])
        bitstream.post(test_client, item_handle=item.handle)
        response = test_client.delete(f"/bitstreams/{bitstream.uuid}")
        assert isinstance(response, requests.Response)
        assert response.status_code == 200


def test_client_get_method(my_vcr, vcr_env):
    with my_vcr.use_cassette("tests/vcr_cassettes/client/status.yaml"):
        client = DSpaceClient(vcr_env["url"], verify=vcr_env["verify"])
        response = client.get("/status")
        assert isinstance(response, requests.Response)


def test_client_get_object_by_handle(my_vcr, test_client, vcr_env):
    with my_vcr.use_cassette("tests/vcr_cassettes/client/get_object_by_handle.yaml"):
        collection = test_client.get_object_by_handle(vcr_env["test_collection_handle"]).json()
        assert collection["name"] == vcr_env["test_collection_name"]
        assert collection["type"] == vcr_env["test_collection_type"]
        assert collection["uuid"] == vcr_env["test_collection_uuid"]


def test_client_get_object_by_handle_raises_error_if_doesnt_exist(
    my_vcr, test_client, vcr_env
):
    with my_vcr.use_cassette(
        "tests/vcr_cassettes/client/get_object_by_handle_doesnt_exist.yaml"
    ):
        with pytest.raises(requests.HTTPError):
            test_client.get_object_by_handle("1721.1/000000")


def test_client_login(my_vcr, vcr_env):
    with my_vcr.use_cassette("tests/vcr_cassettes/client/login.yaml"):
        client = DSpaceClient(vcr_env["url"], verify=vcr_env["verify"])
        assert "JSESSIONID" not in client.cookies
        client.login(vcr_env["email"], vcr_env["password"])
        assert "JSESSIONID" in client.cookies


def test_client_login_raises_auth_error(my_vcr, vcr_env):
    with my_vcr.use_cassette("tests/vcr_cassettes/client/login_error.yaml"):
        client = DSpaceClient(vcr_env["url"], verify=vcr_env["verify"])
        with pytest.raises(requests.HTTPError):
            client.login("fake_user@example.com", "fake_password")


def test_client_post_method(my_vcr, vcr_env):
    with my_vcr.use_cassette("tests/vcr_cassettes/client/login.yaml"):
        client = DSpaceClient(vcr_env["url"], verify=vcr_env["verify"])
        response = client.post(
            "/login", data={"email": vcr_env["email"], "password": vcr_env["password"]}
        )
        assert isinstance(response, requests.Response)


def test_client_status(my_vcr, test_client, vcr_env):
    with my_vcr.use_cassette("tests/vcr_cassettes/client/status.yaml"):
        status = test_client.status().json()
        assert status["okay"] is True
        assert status["authenticated"] is True
