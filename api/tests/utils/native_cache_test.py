import json
from unittest import mock

import pydantic as pydantic_v2
import pytest
import redis

from pcapi import settings
from pcapi.routes.native.v3.serialization.offers import OfferResponse
from pcapi.utils import native_cache


BODY = json.dumps({"id": 42, "name": "Offer"})


class FakeRedis:
    def __init__(self, get_error=None, set_error=None):
        self.store = {}
        self.ttls = {}
        self.get_error = get_error
        self.set_error = set_error

    def get(self, key):
        if self.get_error:
            raise self.get_error
        return self.store.get(key)

    def set(self, key, value, ex=None):
        if self.set_error:
            raise self.set_error
        self.store[key] = value
        self.ttls[key] = ex


@pytest.fixture(name="enabled_cache")
def enabled_cache_fixture(monkeypatch):
    monkeypatch.setattr(settings, "REDIS_CACHE_URL", "redis://cache:6379")
    monkeypatch.setattr(settings, "REDIS_CACHE_TTL_SECONDS", 30)


def _use_client(monkeypatch, client):
    monkeypatch.setattr(native_cache, "_get_client", lambda: client)


def _count(result):
    return native_cache.cache_requests_counter.labels(endpoint="get_offer_v3", result=result)._value.get()


class GetOrComputeTest:
    @pytest.mark.parametrize("url,ttl", [("", 30), ("redis://cache:6379", 0)])
    def test_disabled_without_url_or_ttl(self, monkeypatch, url, ttl):
        monkeypatch.setattr(settings, "REDIS_CACHE_URL", url)
        monkeypatch.setattr(settings, "REDIS_CACHE_TTL_SECONDS", ttl)
        client = mock.Mock()
        _use_client(monkeypatch, client)

        assert native_cache.get_or_compute("get_offer_v3", "key", lambda: BODY) == BODY
        assert not client.mock_calls

    def test_miss_computes_and_stores_with_ttl(self, monkeypatch, enabled_cache):
        client = FakeRedis()
        _use_client(monkeypatch, client)
        misses = _count("miss")

        assert native_cache.get_or_compute("get_offer_v3", "key", lambda: BODY) == BODY
        assert client.store == {"key": BODY}
        assert client.ttls == {"key": 30}
        assert _count("miss") == misses + 1

    def test_hit_serves_stored_body_without_computing(self, monkeypatch, enabled_cache):
        client = FakeRedis()
        client.store["key"] = BODY
        _use_client(monkeypatch, client)
        compute = mock.Mock()
        hits = _count("hit")

        assert native_cache.get_or_compute("get_offer_v3", "key", compute) == BODY
        compute.assert_not_called()
        assert _count("hit") == hits + 1

    @pytest.mark.parametrize(
        "error",
        [
            redis.TimeoutError(),
            redis.ConnectionError(),
            redis.AuthenticationError(),
            UnicodeDecodeError("utf-8", b"", 0, 1, ""),
        ],
    )
    def test_get_error_falls_back_to_database(self, monkeypatch, enabled_cache, error):
        """The cache must never make a request fail: any error serves the response computed from the database."""
        _use_client(monkeypatch, FakeRedis(get_error=error))
        errors = _count("error")

        assert native_cache.get_or_compute("get_offer_v3", "key", lambda: BODY) == BODY
        assert _count("error") == errors + 1

    def test_unreadable_entry_falls_back_to_database(self, monkeypatch, enabled_cache):
        client = FakeRedis()
        client.store["key"] = "{not json"
        _use_client(monkeypatch, client)

        assert native_cache.get_or_compute("get_offer_v3", "key", lambda: BODY) == BODY

    def test_set_error_still_serves_computed_body(self, monkeypatch, enabled_cache):
        _use_client(monkeypatch, FakeRedis(set_error=redis.TimeoutError()))
        errors = _count("error")

        assert native_cache.get_or_compute("get_offer_v3", "key", lambda: BODY) == BODY
        assert _count("error") == errors + 1

    def test_compute_error_is_not_cached(self, monkeypatch, enabled_cache):
        client = FakeRedis()
        _use_client(monkeypatch, client)

        def compute():
            raise ValueError("not found")

        with pytest.raises(ValueError):
            native_cache.get_or_compute("get_offer_v3", "key", compute)
        assert client.store == {}


class BuildKeyTest:
    def test_key_format(self):
        key = native_cache.build_key("get_offer_v3", "v3", OfferResponse, 42)

        assert key == f"native:get_offer_v3:v3:{native_cache.get_schema_hash(OfferResponse)}:42"

    def test_schema_change_changes_key(self):
        """A response format change must change every key, so that two API versions never share an entry."""

        class Response(pydantic_v2.BaseModel):
            id: int

        class ChangedResponse(pydantic_v2.BaseModel):
            id: int
            name: str

        assert native_cache.get_schema_hash(Response) != native_cache.get_schema_hash(ChangedResponse)

    def test_offer_response_schema_hash_is_frozen(self):
        """Update this value only on purpose: it changes when the offer detail response format changes."""
        assert native_cache.get_schema_hash(OfferResponse) == "8326f10c4bcd"
