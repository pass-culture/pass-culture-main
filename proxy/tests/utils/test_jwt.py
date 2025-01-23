import datetime

from fastapi.exceptions import HTTPException
import jwt
import pytest

from pcproxy import settings
from pcproxy.utils.jwt import JWTUserId


@pytest.mark.asyncio
async def test_token_ok():
    user_id = 123
    token = jwt.encode(
        payload={
            "iat": int((datetime.datetime.now() - datetime.timedelta(seconds=10)).timestamp()),
            "nbf": int((datetime.datetime.now() - datetime.timedelta(seconds=10)).timestamp()),
            "exp": int((datetime.datetime.now() + datetime.timedelta(seconds=10)).timestamp()),
            "user_claims": {"user_id": user_id},
        },
        key=settings.JWT_SECRET_KEY,
        algorithm="HS256",
    )
    result = await JWTUserId(authorization=f"Bearer {token}")
    assert result == user_id


@pytest.mark.asyncio
async def test_expired_token():
    token = jwt.encode(
        payload={
            "iat": int(datetime.datetime.now().timestamp()),
            "nbf": int(datetime.datetime.now().timestamp()),
            "exp": int((datetime.datetime.now() - datetime.timedelta(seconds=10)).timestamp()),
            "user_claims": {"user_id": 123},
        },
        key=settings.JWT_SECRET_KEY,
        algorithm="HS256",
    )
    with pytest.raises(HTTPException) as exp_info:
        await JWTUserId(authorization=f"Bearer {token}")

    assert exp_info.value.status_code == 401
    assert exp_info.value.detail == "Expired JWT"


@pytest.mark.asyncio
async def test_invalid_token():
    token = jwt.encode(
        payload={
            "iat": int(datetime.datetime.now().timestamp()),
            "nbf": int(datetime.datetime.now().timestamp()),
            "exp": int((datetime.datetime.now() + datetime.timedelta(seconds=10)).timestamp()),
            "user_claims": {"user_id": 123},
        },
        key="INVALID_SECRET",
        algorithm="HS256",
    )
    with pytest.raises(HTTPException) as exp_info:
        await JWTUserId(authorization=f"Bearer {token}")

    assert exp_info.value.status_code == 401
    assert exp_info.value.detail == "Invalid JWT"


@pytest.mark.asyncio
async def test_no_token():
    result = await JWTUserId(authorization=None)
    assert result is None
