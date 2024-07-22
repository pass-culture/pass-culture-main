import json

from pcapi.core import testing


class UniversalLinksTest:
    def test_apple_app_site_asso(self, client):
        with testing.assert_num_queries(0):
            response = client.get("/.well-known/apple-app-site-association")
            assert response.status_code == 200
        assert response.content_type == "application/pkcs7-mime"
        assert "applinks" in json.loads(response.data.decode("utf8"))

    def test_asset_links(self, client):
        with testing.assert_num_queries(0):
            response = client.get("/.well-knwon/assetlinks.json")
            assert response.status_code == 200
        assert response.content_type == "application/pkcs7-mime"
        assert json.loads(response.data.decode("utf8"))[0]["target"]["package_name"] == "com.passculture"
