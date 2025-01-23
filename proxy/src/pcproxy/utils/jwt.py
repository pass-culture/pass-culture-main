from typing import Annotated

import fastapi
import jwt

from pcproxy import settings


async def JWTUserId(authorization: Annotated[str | None, fastapi.Header()] = None) -> int | None:
    user_id = None
    if authorization and len(authorization) > 8:
        try:
            token = jwt.decode(
                # remove "Bearer "
                authorization[7:],
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"],
            )
        except jwt.exceptions.ExpiredSignatureError:
            raise fastapi.HTTPException(status_code=401, detail="Expired JWT")
        except jwt.exceptions.InvalidSignatureError:
            raise fastapi.HTTPException(status_code=401, detail="Invalid JWT")
        except Exception:
            raise fastapi.HTTPException(status_code=401, detail="Invalid JWT")

        user_id = token.get("user_claims", {}).get("user_id", None)

    return user_id
