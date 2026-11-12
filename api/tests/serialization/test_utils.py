import datetime

import pytest
import pytz

from pcapi.serialization.utils import as_utc_without_timezone
from pcapi.serialization.utils import check_url


class CheckUrlTest:
    @pytest.mark.parametrize(
        "url",
        [
            "http://localhost/test",
            "https://google.fr@evil.com/",
            "https://10.0.0.1/?google.fr",
            "https://metadata.goog/",
            "https://127.0.0.1:5000/?test",
            "https://test.internal:8080/",
            "http://fe80::eb8d:f350:19bb:3f74/",
            "http://0.0.0.0:80",
            "http://[::]:80/",
            "http://[0000::1]:80/",
            "http://[0:0:0:0:0:ffff:127.0.0.1]",
            "http://[::ffff:127.0.0.1]",
            "http://0/",
            "http://127.1",
            "http://2130706433/",
            "http://3232235521/",
            "http://192.168.0.1",
            "http://0177.0.0.1/",
            "http://o177.0.0.1/",
            "http://0o177.0.0.1/",
            "http://q177.0.0.1/",
            "http://0xa9fea9fe",
            "http://ip6-loopback",
            "http:127.0.0.1/",
            "file:///etc/passwd",
            "http://test.localhost",
            "http://test.localhost.",
            "http://test.localhost..",
            "http://test.localhost...",
            "http://example.com/test/../toto",
            "http://127-0-0-1.in-addr.arpa",
            "https://example.com:8080",
            "FILE://example.com/",
        ],
    )
    def test_rejected_url(self, url):
        with pytest.raises(ValueError):
            check_url(url, pydantic_version="v1")

    @pytest.mark.parametrize(
        "url",
        [
            "http://example.com/test",
            "http://example.com/test?arg=127.0.0.1",
            "https://example.com/test",
            "https://example.com",
            "https://some.very.42.long.chain.of.subdomains.example.com",
        ],
    )
    def test_accepted_url(self, url):
        assert check_url(url, pydantic_version="v1")


class AsUtcWithoutTimezoneTest:
    def test_converts_aware_datetime_to_naive_utc(self):
        paris_datetime = pytz.timezone("Europe/Paris").localize(datetime.datetime(2026, 7, 14, 22, 0))

        assert as_utc_without_timezone(paris_datetime) == datetime.datetime(2026, 7, 14, 20, 0)

    @pytest.mark.parametrize(
        "value",
        [
            datetime.datetime(9999, 12, 31, 21, 59, 59),
            datetime.datetime(9999, 12, 31, 23, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=-5))),
        ],
    )
    def test_returns_max_datetime_when_conversion_goes_beyond_year_9999(self, value):
        # PC-44463: the conversion raised "ValueError: year 10000 is out of range"
        assert as_utc_without_timezone(value) == datetime.datetime.max

    @pytest.mark.parametrize(
        "value",
        [
            datetime.datetime(1, 1, 1, 0, 0),
            datetime.datetime(1, 1, 1, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=5))),
        ],
    )
    def test_returns_min_datetime_when_conversion_goes_before_year_1(self, value):
        assert as_utc_without_timezone(value) == datetime.datetime.min
