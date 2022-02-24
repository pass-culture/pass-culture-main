import time

# Re-use the same logger since we log the exact same message.
from pcapi.utils.requests import logger


SENDINBLUE_REQUEST_TIMEOUT = 5


def custom_restclient_request(self, method, url, **kwargs):
    """Wrapper around ``RESTClientObject.request()`` from SendindBlue SDK
    that sets a default timeout and logs the request.
    """
    start = time.perf_counter()
    # FIXME (dbaty, 2022-02-21): once we have gathered logs, we can
    # set an appropriate timeout value with the following line:
    # kwargs.setdefault("_request_timeout", SENDINBLUE_REQUEST_TIMEOUT)
    try:
        response = self.__orig_request(method, url, **kwargs)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception(
            "Call to external service failed with %s",
            # APIException from sib_api_v3_sdk has a status. Other exceptions don't.
            getattr(exc, "status", str(exc)),
            extra={
                "method": method,
                "url": url,
            },
        )
        raise
    else:
        elapsed = time.perf_counter() - start
        logger.info(
            "External service called",
            extra={
                "url": url,
                "statusCode": response.status,
                "duration": elapsed,
            },
        )
    return response


def monkey_patch_sendinblue():
    from sib_api_v3_sdk.rest import RESTClientObject

    RESTClientObject.__orig_request = RESTClientObject.request
    RESTClientObject.request = custom_restclient_request


def install_monkey_patches():
    monkey_patch_sendinblue()
