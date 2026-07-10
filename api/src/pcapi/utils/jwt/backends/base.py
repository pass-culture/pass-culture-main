import abc
import time
import typing


class JwtPayload(typing.TypedDict, total=False):
    nbf: int
    iat: int
    exp: int


class JwtBaseBackend(abc.ABC):
    @staticmethod
    def _complete_payload(payload: dict[str, typing.Any]) -> JwtPayload:
        if "nbf" not in payload:
            payload["nbf"] = int(time.time())
        if "iat" not in payload:
            payload["iat"] = payload["nbf"]
        if "exp" not in payload:
            payload["exp"] = payload["nbf"] + 20 * 60  # default 20 minutes validity

        return typing.cast(JwtPayload, payload)

    @abc.abstractmethod
    def encode(self, payload: dict, key: str | None = None) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def decode(self, jwt_token: str, key: str | None = None) -> dict:
        raise NotImplementedError()
