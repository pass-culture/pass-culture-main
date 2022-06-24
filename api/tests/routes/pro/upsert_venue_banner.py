import io
import pathlib
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.core import testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.utils.human_ids import humanize

import tests


pytestmark = pytest.mark.usefixtures("db_session")
IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


class Returns201Test:
    @freeze_time("2020-10-15 00:00:00")
    @patch("pcapi.core.search.async_index_venue_ids")
    def test_upload_image(self, mock_search_async_index_venue_ids, client, tmpdir):
        """
        Check that the image upload works for a legit file (size and type):
            * API returns a 201 status code
            * the file has been saved to disk (and resized/cropped before that)
            * venue's banner information have been updated
            * venue's banner information are sent back to the client
        """
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        image_content = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        file = {"banner": (io.BytesIO(image_content), "upsert_banner.jpg")}

        client = client.with_session_auth(email=user_offerer.user.email)
        url = f"/venues/{humanize(venue.id)}/banner"
        url += "?x_crop_percent=0.0&y_crop_percent=0.0&height_crop_percent=0.6&width_crop_percent=0.9&image_credit=none"

        # Override storage url otherwise it would be, well, an URL
        # (like http://localhost) and make some checks more difficult.
        # Override local storage and use a temporary directory instead.
        with testing.override_settings(
            OBJECT_STORAGE_URL=tmpdir.dirname, LOCAL_STORAGE_DIR=pathlib.Path(tmpdir.dirname)
        ):
            response = client.post(url, files=file)
            assert response.status_code == 201

            url_prefix = pathlib.Path(tmpdir.dirname) / "thumbs" / "venues"

            banner_url_timestamp = 1602720000
            assert response.json["bannerUrl"] == str(url_prefix / f"{humanize(venue.id)}_{banner_url_timestamp}")

            original_banner_url_timestamp = 1602720001
            assert response.json["bannerMeta"] == {
                "image_credit": "none",
                "original_image_url": str(url_prefix / f"{humanize(venue.id)}_{original_banner_url_timestamp}"),
                "crop_params": {
                    "x_crop_percent": 0.0,
                    "y_crop_percent": 0.0,
                    "height_crop_percent": 0.6,
                    "width_crop_percent": 0.9,
                },
            }


class Returns400Test:
    def test_upload_image_missing(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        client = client.with_session_auth(email=user_offerer.user.email)
        url = f"/venues/{humanize(venue.id)}/banner"
        response = client.post(url)

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_BANNER_CONTENT"

    def test_upload_image_invalid_query_param(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        url = f"/venues/{humanize(venue.id)}/banner"
        url += "?x_crop_percent=0.8&y_crop_percent=invalid_value"

        image_content = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        file = {"banner": (io.BytesIO(image_content), "upsert_banner.jpg")}

        client = client.with_session_auth(email=user_offerer.user.email)
        response = client.post(url, files=file)

        assert response.status_code == 400
        assert response.json["code"] == "INVALID_BANNER_PARAMS"

    def test_upload_image_bad_ratio(self, client, tmpdir):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        # this image is too small to be resized and has a 1:1 ratio
        # it should be rejected
        image_content = (IMAGES_DIR / "mouette_small.jpg").read_bytes()
        file = {"banner": (io.BytesIO(image_content), "upsert_banner.jpg")}

        client = client.with_session_auth(email=user_offerer.user.email)
        url = f"/venues/{humanize(venue.id)}/banner"
        url += "?x_crop_percent=0.0&y_crop_percent=0.0&height_crop_percent=1.0&width_crop_percent=1.0&image_credit=none"

        # Override storage url otherwise it would be, well, an URL
        # (like http://localhost) and make some checks more difficult.
        # Override local storage and use a temporary directory instead.
        with testing.override_settings(
            OBJECT_STORAGE_URL=tmpdir.dirname, LOCAL_STORAGE_DIR=pathlib.Path(tmpdir.dirname)
        ):
            response = client.post(url, files=file)
            assert response.status_code == 400
            assert response.json["code"] == "BAD_IMAGE_RATIO"
