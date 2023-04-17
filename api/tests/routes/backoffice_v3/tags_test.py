from datetime import date
from datetime import datetime
from datetime import timedelta

from flask import g
from flask import url_for
import pytest

import pcapi.core.criteria.factories as criteria_factories
import pcapi.core.criteria.models as criteria_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.permissions.models as perm_models
from pcapi.models import db

from .helpers import html_parser
from .helpers import unauthorized as unauthorized_helpers


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class CreateTagTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        endpoint = "backoffice_v3_web.tags.create_tag"
        needed_permission = perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS

    def test_create_tag(self, authenticated_client):
        form = {"name": "my-tag", "description": "description"}

        response = send_request(authenticated_client, form, "create_tag")

        assert response.status_code == 303
        assert response.location == url_for("backoffice_v3_web.tags.list_tags", _external=True)

        tag = criteria_models.Criterion.query.first()

        assert tag.name == "my-tag"
        assert tag.description == "description"
        assert not tag.startDateTime
        assert not tag.endDateTime


class DeleteTagTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        endpoint = "backoffice_v3_web.tags.delete_tag"
        endpoint_kwargs = {"tag_id": 1}
        needed_permission = perm_models.Permissions.DELETE_OFFERER_TAG

    def test_delete_tag(self, authenticated_client):
        offer = offers_factories.OfferFactory()
        tag = criteria_factories.CriterionFactory()
        offer.criteria = [tag]

        response = send_request(authenticated_client, {}, "delete_tag", tag_id=tag.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_v3_web.tags.list_tags", _external=True)

        assert criteria_models.Criterion.query.count() == 0


class UpdateTagTest:
    class UnauthorizedTest(unauthorized_helpers.UnauthorizedHelperWithCsrf):
        endpoint = "backoffice_v3_web.tags.update_tag"
        endpoint_kwargs = {"tag_id": 1}
        needed_permission = perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS

    def test_update_tag(self, authenticated_client):
        tag = criteria_factories.CriterionFactory(description="desc", startDateTime=None, endDateTime=None)

        new_tag_name = f"{tag.name}-update"
        new_tag_description = f"{tag.description} update"
        new_start_date = date.today()
        new_end_date = new_start_date + timedelta(days=1)

        form = {
            "name": new_tag_name,
            "description": new_tag_description,
            "start_date": new_start_date,
            "end_date": new_end_date,
        }

        response = send_request(authenticated_client, form, "update_tag", tag_id=tag.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_v3_web.tags.list_tags", _external=True)

        db.session.refresh(tag)

        assert tag.name == new_tag_name
        assert tag.description == new_tag_description
        assert tag.startDateTime.date() == new_start_date
        assert tag.endDateTime.date() == new_end_date


class ListTagsTest:
    def test_list_tags(self, authenticated_client):
        offer = offers_factories.OfferFactory()

        now = datetime.utcnow()
        tag_1 = criteria_factories.CriterionFactory(description="tag1 description", startDateTime=now)
        tag_2 = criteria_factories.CriterionFactory(description="tag2 description", startDateTime=now)

        offer.criteria = [tag_1, tag_2]

        response = authenticated_client.get(url_for("backoffice_v3_web.tags.list_tags"))

        assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)

        assert rows[0]["Nom"] == tag_1.name
        assert rows[0]["Description"] == tag_1.description
        assert rows[0]["Date de début"] == tag_1.startDateTime.strftime("%d/%m/%Y")
        assert rows[0]["Date de fin"] == ""

    @pytest.mark.parametrize(
        "q,expected_nb_results,expected_results_key",
        [
            ("", 2, ["tag1", "tag2"]),
            ("tag1", 1, ["tag1"]),
            ("tag2", 1, ["tag2"]),
            ("DésCrIpTion", 2, ["tag1", "tag2"]),
            ("Not found", 0, []),
        ],
    )
    def search_list_tags(self, authenticated_client, q, expected_nb_results, expected_results_key):
        offer = offers_factories.OfferFactory()

        tags = {
            "tag1": criteria_factories.CriterionFactory(
                description="tag1 description", startDateTime=datetime.utcnow()
            ),
            "tag2": criteria_factories.CriterionFactory(
                description="tag2 description", startDateTime=datetime.utcnow()
            ),
        }

        offer.criteria = [tags["tag1"], tags["tag2"]]

        response = authenticated_client.get(url_for("backoffice_v3_web.tags.list_tags", q=q))

        assert response.status_code == 200

        nb_results = html_parser.count_table_rows(response.data)
        assert nb_results == expected_nb_results

        rows = html_parser.extract_table_rows(response.data)
        count = 0
        for index, key in enumerate(expected_results_key):
            for row in rows:
                if count < expected_nb_results and row[index]["Nom"] == tags.get(key).name:
                    assert rows[index]["Description"] == tags.get(key).description
                    count += 1
                    break


def send_request(authenticated_client, form, route_suffix, **route_extra):
    authenticated_client.get(url_for("backoffice_v3_web.tags.list_tags"))
    form["csrf_token"] = g.get("csrf_token", "")

    url = url_for(f"backoffice_v3_web.tags.{route_suffix}", **route_extra)
    return authenticated_client.post(url, form=form)
