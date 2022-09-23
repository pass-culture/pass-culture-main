import json
from typing import ByteString
from typing import Optional

from flask import current_app
import pytest

from pcapi.models.feature import Feature
from pcapi.models.feature import PRO_FEATURE_CACHE

from tests.conftest import TestClient
from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_fake_valid_token


@pytest.mark.usefixtures("clear_redis")
@pytest.mark.usefixtures("db_session")
class Returns200Test:
    valid_user = {
        "mail": "sabine.laprof@example.com",
        "uai": "EAU123",
    }

    def _create_adage_valid_token(self, uai_code: Optional[str]) -> ByteString:
        return create_adage_jwt_fake_valid_token(
            civility=self.valid_user.get("civilite"),
            lastname=self.valid_user.get("nom"),
            firstname=self.valid_user.get("prenom"),
            email=self.valid_user.get("mail"),
            uai=uai_code,
        )

    def test_should_create_feature_cache(self, app) -> None:
        redis_client = current_app.redis_client
        # Given
        valid_encoded_token = self._create_adage_valid_token(uai_code=self.valid_user.get("uai"))
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {valid_encoded_token}"}

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
        response = test_client.get("/adage-iframe/features")

        cache = redis_client.get(PRO_FEATURE_CACHE)
        # Then
        assert response.status_code == 200
        assert sorted(response.json, key=lambda x: x["id"]) == expected
        assert sorted(json.loads(cache), key=lambda x: x["id"]) == expected

    def test_should_use_feature_cache(self, app) -> None:
        redis_client = current_app.redis_client
        # Given
        valid_encoded_token = self._create_adage_valid_token(uai_code=self.valid_user.get("uai"))
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {valid_encoded_token}"}
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
        response = test_client.get("/adage-iframe/features")
        cache = redis_client.get(PRO_FEATURE_CACHE)

        # Then
        assert response.status_code == 200
        assert response.json == expected
        assert json.loads(cache) == expected


@pytest.mark.usefixtures("clear_redis")
@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_should_preserve_authentication(self, app) -> None:
        redis_client = current_app.redis_client
        # Given
        test_client = TestClient(app.test_client())
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
        response = test_client.get("/adage-iframe/features")
        cache = redis_client.get(PRO_FEATURE_CACHE)

        # Then
        assert response.status_code == 403
        assert response.json == {
            "Authorization": "Unrecognized token",
        }
        assert json.loads(cache) == expected
