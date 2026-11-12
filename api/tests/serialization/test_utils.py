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

    def test_keeps_naive_datetime_unchanged(self):
        # naive datetimes are already UTC (as stored in the database)
        assert as_utc_without_timezone(datetime.datetime(2026, 7, 14, 22, 0)) == datetime.datetime(2026, 7, 14, 22, 0)

    @pytest.mark.parametrize(
        "naive_datetime",
        [datetime.datetime(9999, 12, 31, 0, 0), datetime.datetime(9999, 12, 31, 21, 59, 59)],
    )
    def test_handles_naive_datetime_on_last_day_of_year_9999(self, naive_datetime):
        # PC-44463: `astimezone` on a naive datetime probes the local timezone 24h around the date,
        # which raised "ValueError: year 10000 is out of range" on 9999-12-31
        assert as_utc_without_timezone(naive_datetime) == naive_datetime
