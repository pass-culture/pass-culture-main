import logging
from unittest.mock import patch

import pytest

from pcapi.core.external.attributes.queue import REDIS_BACKUP_EMAIL_TO_UPDATE
from pcapi.core.external.attributes.queue import REDIS_EMAIL_LIST_ATTRIBUTES_TO_UPDATE
from pcapi.core.external.attributes.queue import add_email_to_async_pro_attributes_update
from pcapi.core.external.attributes.queue import update_pro_attributes


def test_update_pro_attributes(app, clear_redis, caplog):
    add_email_to_async_pro_attributes_update("wilkommen@example.com")
    add_email_to_async_pro_attributes_update("bienvenue@example.com")
    add_email_to_async_pro_attributes_update("welcome@example.com")
    with caplog.at_level(logging.INFO):
        update_pro_attributes()
        assert set(record.extra["email"] for record in caplog.records if record.extra.get("email") is not None) == {
            "wilkommen@example.com",
            "bienvenue@example.com",
            "welcome@example.com",
        }
    assert app.redis_client.smembers(REDIS_EMAIL_LIST_ATTRIBUTES_TO_UPDATE) == set()
    assert app.redis_client.get(REDIS_BACKUP_EMAIL_TO_UPDATE) is None


def test_update_pro_attributes_with_backup(app, clear_redis, caplog):
    app.redis_client.set(REDIS_BACKUP_EMAIL_TO_UPDATE, "nemoubliezpas@example.com")
    add_email_to_async_pro_attributes_update("wilkommen@example.com")
    add_email_to_async_pro_attributes_update("bienvenue@example.com")
    with caplog.at_level(logging.INFO):
        update_pro_attributes()
        assert set(record.extra["email"] for record in caplog.records if record.extra.get("email") is not None) == {
            "wilkommen@example.com",
            "bienvenue@example.com",
            "nemoubliezpas@example.com",
        }
    assert app.redis_client.smembers(REDIS_EMAIL_LIST_ATTRIBUTES_TO_UPDATE) == set()
    assert app.redis_client.get(REDIS_BACKUP_EMAIL_TO_UPDATE) is None


@patch("pcapi.core.external.attributes.queue.get_pro_attributes", side_effect=ValueError)
def test_update_pro_attributes_exception_fills_backup(mock_get_pro_attributes, app, clear_redis, caplog):
    add_email_to_async_pro_attributes_update("wilkommen@example.com")
    add_email_to_async_pro_attributes_update("bienvenue@example.com")

    with caplog.at_level(logging.INFO):
        with pytest.raises(ValueError):
            update_pro_attributes()

    email_that_failed = [record.extra["email"] for record in caplog.records if record.extra.get("email") is not None][0]

    assert app.redis_client.smembers(REDIS_EMAIL_LIST_ATTRIBUTES_TO_UPDATE) == {
        "bienvenue@example.com",
        "wilkommen@example.com",
    } - {email_that_failed}
    assert app.redis_client.get(REDIS_BACKUP_EMAIL_TO_UPDATE) == email_that_failed
