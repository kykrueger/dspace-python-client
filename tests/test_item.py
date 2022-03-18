# tests/test_item.py
import pytest
import requests

from dspace.errors import MissingIdentifierError
from dspace.item import Item, MetadataEntry


def test_item_delete(my_vcr, vcr_env, test_client):
    with my_vcr.use_cassette(
        "tests/vcr_cassettes/item/delete_item.yaml",
    ):
        item = Item(
            metadata=[
                MetadataEntry(key="dc.title", value="Test Item"),
                MetadataEntry(key="dc.contributor.author", value="Jane Q. Author"),
            ]
        )
        item.post(test_client, collection_uuid=vcr_env["test_collection_uuid"])
        item2 = Item()
        item2.uuid = item.uuid
        response = item2.delete(test_client)
        assert isinstance(response, requests.Response)
        assert response.status_code == 200
        assert item2.uuid is None


def test_item_delete_nonexistent_item_raises_error(my_vcr, test_client):
    with my_vcr.use_cassette(
        "tests/vcr_cassettes/item/delete_nonexistent_item.yaml",
    ):
        with pytest.raises(requests.HTTPError):
            item = Item()
            item.uuid = "5-7-4-b-0"
            item.delete(test_client)


def test_item_instantiates_with_expected_values():
    title = MetadataEntry(key="dc.title", value="Test Item")
    item = Item(metadata=[title])
    assert item.bitstreams == []
    assert item.metadata == [title]



def test_item_post_success_with_handle(my_vcr, vcr_env, test_client):
    with my_vcr.use_cassette("tests/vcr_cassettes/item/post_item_with_handle.yaml"):
        item = Item(
            metadata=[
                MetadataEntry(key="dc.title", value="Test Item"),
                MetadataEntry(key="dc.contributor.author", value="Jane Q. Author"),
            ]
        )
        item.post(test_client, collection_handle=vcr_env["test_collection_handle"])
        assert item.archived == "true"
        assert item.parentCollection is None
        assert item.parentCollectionList is None
        assert item.parentCommunityList is None
        assert item.name == "Test Item"
        assert item.withdrawn == "false"


def test_item_post_success_with_uuid(my_vcr, vcr_env, test_client):
    with my_vcr.use_cassette("tests/vcr_cassettes/item/post_item_with_uuid.yaml"):
        item = Item(
            metadata=[
                MetadataEntry(key="dc.title", value="Test Item"),
                MetadataEntry(key="dc.contributor.author", value="Jane Q. Author"),
            ]
        )
        item.post(test_client, collection_uuid=vcr_env["test_collection_uuid"])
        assert item.archived == "true"
        assert item.name == "Test Item"
        assert item.parentCollection is None
        assert item.parentCollectionList is None
        assert item.parentCommunityList is None
        assert item.withdrawn == "false"

def test_item_get_metadata_success(my_vcr, vcr_env, test_client):
    #with my_vcr.use_cassette("tests/vcr_cassettes/item/get_metadata_new_item.yaml"):
    item = Item(
        metadata=[
            MetadataEntry(key="dc.title", value="Test Item"),
            MetadataEntry(key="dc.contributor.author", value="Jane Q. Author"),
        ]
    )
    item.post(test_client, collection_uuid=vcr_env["test_collection_uuid"])
    metadata = item.get_metadata_entries(test_client)
    assert len(metadata) > 0


def test_item_post_to_nonexistent_collection_raises_error(my_vcr, test_client):
    with my_vcr.use_cassette(
        "tests/vcr_cassettes/item/post_to_nonexistent_collection.yaml"
    ):
        with pytest.raises(requests.HTTPError):
            item = Item()
            item.post(test_client, collection_uuid="123456")


def test_item_post_without_handle_or_uuid_raises_error(test_client):
    with pytest.raises(MissingIdentifierError):
        item = Item()
        item.post(test_client)


def test_metadata_entry_instantiates_with_expected_values():
    metadata_entry = MetadataEntry("dc.fieldname", "field value")
    assert metadata_entry.key == "dc.fieldname"
    assert metadata_entry.value == "field value"
    assert metadata_entry.language is None


def test_metadata_entry_to_dict():
    metadata_entry = MetadataEntry("dc.fieldname", "field value")
    metadata_entry_dict = metadata_entry.to_dict()
    assert metadata_entry_dict == {"key": "dc.fieldname", "value": "field value"}


def test_metadata_entry_from_dict():
    test_entry = {"key": "dc.fieldname", "value": "field value"}
    metadata_entry = MetadataEntry.from_dict(test_entry)
    assert isinstance(metadata_entry, MetadataEntry)
    assert metadata_entry.key == "dc.fieldname"
    assert metadata_entry.value == "field value"
    assert metadata_entry.language is None


def test_metadata_entry_from_dict_raises_error_if_missing_fields():
    with pytest.raises(KeyError):
        test_entry = {"value": "field value"}
        MetadataEntry.from_dict(test_entry)
        MetadataEntry.from_dict(test_entry)
