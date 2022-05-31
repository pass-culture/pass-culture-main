from datetime import datetime
import io
import pathlib

import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import override_settings
from pcapi.utils.human_ids import humanize

import tests


pytestmark = pytest.mark.usefixtures("db_session")


class FormatQueryParamsTest:
    def test_format_params(self, app):
        with app.app_context():
            from pcapi.routes.error_handlers.utils import format_sql_statement_params
        sqla_params = {
            "token_1": "E3PGVS",
            "lower_1": "pctest.jeune93.has-booked-some.v1@example.com",
            "id_1": 270,
            "date_1": datetime(2021, 1, 1, 12, 0, 10),
            "list_1": [datetime(2021, 1, 1), 270, "E3PGVS"],
        }

        formatted_pararms = format_sql_statement_params(sqla_params)

        assert formatted_pararms == {
            "token_1": "'E3PGVS'",
            "lower_1": "'pctest.jeune93.has-booked-some.v1@example.com'",
            "id_1": 270,
            "date_1": "'2021-01-01 12:00:10'",
            "list_1": ["'2021-01-01 00:00:00'", 270, "'E3PGVS'"],
        }


class ImageRatioErrorTest:
    def should_catch_error(self, client, tmpdir):
        with override_settings(OBJECT_STORAGE_URL=tmpdir.dirname, LOCAL_STORAGE_DIR=pathlib.Path(tmpdir.dirname)):
            user_offerer = offerers_factories.UserOffererFactory()
            venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

            images_dir = pathlib.Path(tests.__path__[0]) / "files"

            image_content = (images_dir / "mouette_small.jpg").read_bytes()
            file = {"banner": (io.BytesIO(image_content), "upsert_banner.jpg")}

            url = f"/venues/{humanize(venue.id)}/banner"
            url += (
                "?x_crop_percent=0.0"
                "&y_crop_percent=0.0"
                "&height_crop_percent=0.1"
                "&width_crop_percent=1.0"
                "&image_credit=none"
            )

            client = client.with_session_auth(email=user_offerer.user.email)

            response = client.post(url, files=file)

            assert response.status_code == 400
            assert response.json["code"] == "BAD_IMAGE_RATIO"
