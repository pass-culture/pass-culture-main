import pytest

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
