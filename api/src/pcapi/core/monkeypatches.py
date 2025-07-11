import typing

import brevo_python.rest

# Re-use the same logger since we log the exact same message.
from pcapi.utils.requests import logger


SENDINBLUE_REQUEST_TIMEOUT = 10


def custom_restclient_request(
    self: brevo_python.rest.RESTClientObject,
    method: str,
    url: str,
    **kwargs: typing.Any,
) -> brevo_python.rest.RESTResponse:
    """Wrapper around ``RESTClientObject.request()`` from SendindBlue SDK
    that sets a default timeout and logs the request.
    """
    if kwargs.get("_request_timeout") is None:
        kwargs["_request_timeout"] = SENDINBLUE_REQUEST_TIMEOUT
    try:
        response = self.__orig_request(method, url, **kwargs)
    except Exception as exc:
        logger.warning(
            "Call to external service failed with %s",
            # APIException from brevo_python has a status. Other exceptions don't.
            getattr(exc, "status", str(exc)),
            extra={
                "method": method,
                "url": url,
            },
        )
        raise
    return response


def monkey_patch_sendinblue() -> None:
    from brevo_python.rest import RESTClientObject

    RESTClientObject.__orig_request = RESTClientObject.request
    RESTClientObject.request = custom_restclient_request


def install_monkey_patches() -> None:
    monkey_patch_sendinblue()

    from spectree import _pydantic

    _pydantic.PYDANTIC2 = False
