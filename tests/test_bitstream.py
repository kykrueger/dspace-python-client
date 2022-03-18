# tests/test_bitstream.py
import pytest
import requests

from dspace.bitstream import Bitstream
from dspace.errors import MissingFilePathError, MissingIdentifierError
from dspace.item import Item, MetadataEntry


def test_bitstream_delete(my_vcr, vcr_env, test_client, test_file_path_01):
    with my_vcr.use_cassette(
        "tests/vcr_cassettes/bitstream/delete_bitstream.yaml",
    ):
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
        bitstream2 = Bitstream()
        bitstream2.uuid = bitstream.uuid
        response = bitstream.delete(test_client)
        assert isinstance(response, requests.Response)
        assert response.status_code == 200
        assert bitstream.uuid is None


def test_bitstream_delete_nonexistent_bitstream_raises_error(my_vcr, test_client):
    with my_vcr.use_cassette(
        "tests/vcr_cassettes/bitstream/delete_nonexistent_bitstream.yaml",
    ):
        with pytest.raises(requests.HTTPError):
            bitstream = Bitstream()
            bitstream.uuid = "5-7-4-b-0"
            bitstream.delete(test_client)


def test_bitstream_post_success_remote_file(my_vcr, vcr_env, test_client, mocked_s3):
    with my_vcr.use_cassette(
        "tests/vcr_cassettes/bitstream/post_bitstream_success_remote_file.yaml",
        filter_post_data_parameters=None,
    ):
        bitstream = Bitstream(
            name="test-file-03.txt",
            description="A test TXT file",
            file_path="s3://test-bucket/path/file/test-file-03.txt",
        )
        item = Item(
            metadata=[
                MetadataEntry(key="dc.title", value="Test Item for Bitstream"),
                MetadataEntry(key="dc.contributor.author", value="Jane Doe. Author"),
            ]
        )
        item.post(test_client, collection_handle=vcr_env["test_collection_handle"])
        bitstream.post(test_client, item_handle=item.handle)
        assert bitstream.bundleName == "ORIGINAL"
        assert bitstream.checkSum == {
            "value": "8bfa8e0684108f419933a5995264d150",
            "checkSumAlgorithm": "MD5",
        }
        assert bitstream.format == "Text"
        assert bitstream.link is not None
        assert bitstream.mimeType == "text/plain"
        assert bitstream.parentObject is None
        assert bitstream.policies is None
        assert bitstream.retrieveLink is not None
        assert bitstream.sequenceId == -1
        assert bitstream.sizeBytes == 12
        assert bitstream.uuid is not None


def test_bitstream_post_success_with_handle(my_vcr, vcr_env, test_client, test_file_path_01):
    with my_vcr.use_cassette(
        "tests/vcr_cassettes/bitstream/post_bitstream_with_handle.yaml",
        filter_post_data_parameters=None,
    ):
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
        assert bitstream.bundleName == "ORIGINAL"
        assert bitstream.checkSum == {
            "value": "a4e0f4930dfaff904fa3c6c85b0b8ecc",
            "checkSumAlgorithm": "MD5",
        }
        assert bitstream.format == "Adobe PDF"
        assert bitstream.link is not None
        assert bitstream.mimeType == "application/pdf"
        assert bitstream.parentObject is None
        assert bitstream.policies is None
        assert bitstream.retrieveLink is not None
        assert bitstream.sequenceId == -1
        assert bitstream.sizeBytes == 35721
        assert bitstream.uuid is not None


def test_bitstream_post_success_with_uuid(my_vcr, vcr_env, test_client, test_file_path_01):
    with my_vcr.use_cassette(
        "tests/vcr_cassettes/bitstream/post_bitstream_with_uuid.yaml",
        filter_post_data_parameters=None,
    ):
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
        bitstream.post(test_client, item_uuid=item.uuid)
        assert bitstream.bundleName == "ORIGINAL"
        assert bitstream.checkSum == {
            "value": "a4e0f4930dfaff904fa3c6c85b0b8ecc",
            "checkSumAlgorithm": "MD5",
        }
        assert bitstream.format == "Adobe PDF"
        assert bitstream.link is not None
        assert bitstream.mimeType == "application/pdf"
        assert bitstream.parentObject is None
        assert bitstream.policies is None
        assert bitstream.retrieveLink is not None
        assert bitstream.sequenceId == -1
        assert bitstream.sizeBytes == 35721
        assert bitstream.uuid is not None


def test_bitstream_post_to_nonexistent_item_raises_error(
    my_vcr, test_client, test_file_path_01
):
    with my_vcr.use_cassette(
        "tests/vcr_cassettes/bitstream/post_to_nonexistent_item.yaml",
        filter_post_data_parameters=None,
    ):
        with pytest.raises(requests.HTTPError):
            bitstream = Bitstream(file_path=test_file_path_01)
            bitstream.post(test_client, item_uuid="123456")


def test_bitstream_post_without_file_path_raises_error(test_client, test_file_path_01):
    with pytest.raises(MissingFilePathError):
        bitstream = Bitstream()
        bitstream.post(test_client, item_handle="1721.1/131167")


def test_bitstream_post_without_handle_or_uuid_raises_error(
    test_client, test_file_path_01
):
    with pytest.raises(MissingIdentifierError):
        bitstream = Bitstream(file_path=test_file_path_01)
        bitstream.post(test_client)
