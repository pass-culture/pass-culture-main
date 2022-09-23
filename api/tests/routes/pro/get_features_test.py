import json

from flask import current_app
import pytest

from pcapi.core.users import factories as users_factories
from pcapi.models.feature import Feature
from pcapi.models.feature import PRO_FEATURE_CACHE


@pytest.mark.usefixtures("clear_redis")
@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_should_create_feature_cache(self, client) -> None:
        redis_client = current_app.redis_client
        # Given
        user = users_factories.UserFactory()

        expected = []
        assert redis_client.get(PRO_FEATURE_CACHE) == None
        for feature in Feature.query.order_by(Feature.id).all():
            expected.append(
                {
                    "description": feature.description,
                    "id": str(feature.id),
                    "isActive": feature.isActive,
                    "name": feature.name,
                    "nameKey": feature.nameKey,
                }
            )
        # When
        response = client.with_session_auth(user.email).get("/features")

        cache = redis_client.get(PRO_FEATURE_CACHE)
        # Then
        assert response.status_code == 200
        assert sorted(response.json, key=lambda x: x["id"]) == expected
        assert sorted(json.loads(cache), key=lambda x: x["id"]) == expected

    def test_should_use_feature_cache(self, client) -> None:
        redis_client = current_app.redis_client
        # Given
        user = users_factories.UserFactory()
        expected = [
            {
                "description": "description1",
                "id": "1",
                "isActive": True,
                "name": "namé1",
                "nameKey": "nameKey1",
            },
            {
                "description": "description2",
                "id": "2",
                "isActive": False,
                "name": "name2",
                "nameKey": "nameKey2",
            },
            {
                "description": "description3",
                "id": "3",
                "isActive": True,
                "name": "name3",
                "nameKey": "nameKey3",
            },
        ]

        redis_client.set(PRO_FEATURE_CACHE, json.dumps(expected))
        # When
        response = client.with_session_auth(user.email).get("/features")
        cache = redis_client.get(PRO_FEATURE_CACHE)

        # Then
        assert response.status_code == 200
        assert response.json == expected
        assert json.loads(cache) == expected

    def when_user_is_not_logged_in(self, client) -> None:
        redis_client = current_app.redis_client
        # Given

        expected = []
        assert redis_client.get(PRO_FEATURE_CACHE) == None
        for feature in Feature.query.order_by(Feature.id).all():
            expected.append(
                {
                    "description": feature.description,
                    "id": str(feature.id),
                    "isActive": feature.isActive,
                    "name": feature.name,
                    "nameKey": feature.nameKey,
                }
            )
        # When
        response = client.get("/features")

        cache = redis_client.get(PRO_FEATURE_CACHE)
        # Then
        assert response.status_code == 200
        assert sorted(response.json, key=lambda x: x["id"]) == expected
        assert sorted(json.loads(cache), key=lambda x: x["id"]) == expected
