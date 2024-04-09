from unittest import mock

import pytest

from pcapi.utils import kubernetes


@pytest.mark.parametrize(
    "hostname,expected_deployment",
    [
        ("staging-pcapi-api-1a23bc45d6-fghi7", "api"),
        ("staging-pcapi-api-v1-1a23bc45d6-fghi7", "api-v1"),
        ("staging-pcapi-a-really-long-name-1a23bc45d6-fghi7", "a-really-long-name"),
        ("mylocalhost", "mylocalhost"),
        ("my-local-host", "host"),  # it's as good as anything else
    ],
)
def test_get_deployment(hostname, expected_deployment):
    with mock.patch("socket.gethostname", lambda: hostname):
        assert kubernetes.get_deployment() == expected_deployment
