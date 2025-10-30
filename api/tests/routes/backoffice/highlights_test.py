import datetime
import pathlib

import pytest
from flask import url_for

from pcapi.core.highlights import factories as highlights_factories
from pcapi.core.highlights import models as highlights_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db

import tests

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class ListHighlightsTest(GetEndpointHelper):
    endpoint = "backoffice_web.highlights.list_highlights"
    needed_permission = perm_models.Permissions.READ_HIGHLIGHT
    # session
    # current user
    # list highlights
    # count highlights
    expected_num_queries = 4

    def test_without_filters(self, authenticated_client):
        highlight_1 = highlights_factories.HighlightFactory()
        highlight_2 = highlights_factories.HighlightFactory()
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["ID"] == str(highlight_2.id)
        assert rows[0]["Nom"] == highlight_2.name
        assert rows[0]["Description"] == highlight_2.description
        assert (
            rows[0]["Diffusion espace partenaire"]
            == f"{highlight_2.availability_timespan.lower.strftime('%d/%m/%Y')} → {highlight_2.availability_timespan.upper.strftime('%d/%m/%Y')}"
        )
        assert (
            rows[0]["Date(s) d'évènement"]
            == f"{highlight_2.highlight_timespan.lower.strftime('%d/%m/%Y')} → {highlight_2.highlight_timespan.upper.strftime('%d/%m/%Y')}"
        )

        assert rows[1]["ID"] == str(highlight_1.id)
        assert rows[1]["Nom"] == highlight_1.name
        assert rows[1]["Description"] == highlight_1.description
        assert (
            rows[1]["Diffusion espace partenaire"]
            == f"{highlight_1.availability_timespan.lower.strftime('%d/%m/%Y')} → {highlight_1.availability_timespan.upper.strftime('%d/%m/%Y')}"
        )
        assert (
            rows[1]["Date(s) d'évènement"]
            == f"{highlight_1.highlight_timespan.lower.strftime('%d/%m/%Y')} → {highlight_1.highlight_timespan.upper.strftime('%d/%m/%Y')}"
        )

    def test_search_by_content(self, authenticated_client):
        highlight_to_find = highlights_factories.HighlightFactory(
            name="Highlight to find",
        )
        highlights_factories.HighlightFactory()
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, q="hiGh"),
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)

        assert len(rows) == 1
        assert rows[0]["ID"] == str(highlight_to_find.id)


class GetCreateHighlightFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.highlights.get_create_highlight_form"
    needed_permission = perm_models.Permissions.MANAGE_HIGHLIGHT

    # session + current user
    expected_num_queries = 2

    def test_get_create_highlight_form(self, authenticated_client):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200


class CreateHighlightTest(PostEndpointHelper):
    endpoint = "backoffice_web.highlights.create_highlight"
    needed_permission = perm_models.Permissions.MANAGE_HIGHLIGHT

    # - authenticated user
    # - user session
    # - insert into highlight or rollback
    expected_num_queries = 3

    def test_create_highlight(self, authenticated_client):
        name = "New highlight"
        description = "Highlight description"
        highlight_date_from = datetime.date.today() + datetime.timedelta(days=11)
        highlight_date_to = datetime.date.today() + datetime.timedelta(days=12)
        availability_date_from = datetime.date.today() - datetime.timedelta(days=10)
        availability_date_to = datetime.date.today() + datetime.timedelta(days=10)
        separator = " - "

        image_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(image_path, "rb") as image_file:
            response = self.post_to_endpoint(
                authenticated_client,
                form={
                    "name": name,
                    "description": description,
                    "availability_timespan": f"{availability_date_from.strftime('%d/%m/%Y')}{separator}{availability_date_to.strftime('%d/%m/%Y')}",
                    "highlight_timespan": f"{highlight_date_from.strftime('%d/%m/%Y')}{separator}{highlight_date_to.strftime('%d/%m/%Y')}",
                    "image": image_file,
                },
                expected_num_queries=self.expected_num_queries,
            )
            assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert html_parser.extract_alert(response.data) == f"La valorisation thématique {name} a été créée."
        highlight = db.session.query(highlights_models.Highlight).one()
        assert highlight.name == name
        assert highlight.description == description
        assert highlight.availability_timespan.lower == datetime.datetime.combine(
            availability_date_from, datetime.time(0, 0, 0)
        )
        assert highlight.availability_timespan.upper == datetime.datetime.combine(
            availability_date_to, datetime.time(0, 0, 0)
        )
        assert highlight.highlight_timespan.lower == datetime.datetime.combine(
            highlight_date_from, datetime.time(0, 0, 0)
        )
        assert highlight.highlight_timespan.upper == datetime.datetime.combine(
            highlight_date_to, datetime.time(0, 0, 0)
        )

    def test_create_highlight_available_after_highlight(self, authenticated_client):
        name = "New highlight"
        description = "Highlight description"
        highlight_date_from = datetime.date.today() + datetime.timedelta(days=1)
        highlight_date_to = datetime.date.today() + datetime.timedelta(days=2)
        availability_date_from = datetime.date.today() - datetime.timedelta(days=10)
        availability_date_to = datetime.date.today() + datetime.timedelta(days=10)
        separator = " - "

        image_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(image_path, "rb") as image_file:
            response = self.post_to_endpoint(
                authenticated_client,
                form={
                    "name": name,
                    "description": description,
                    "availability_timespan": f"{availability_date_from.strftime('%d/%m/%Y')}{separator}{availability_date_to.strftime('%d/%m/%Y')}",
                    "highlight_timespan": f"{highlight_date_from.strftime('%d/%m/%Y')}{separator}{highlight_date_to.strftime('%d/%m/%Y')}",
                    "image": image_file,
                },
                expected_num_queries=self.expected_num_queries - 1,
            )
            assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == "La diffusion sur l'espace partenaire ne peut pas se terminer après la fin de l'évènement"
        )

    def test_create_highlight_in_the_past(self, authenticated_client):
        name = "New highlight"
        description = "Highlight description"
        highlight_date_from = datetime.date.today() - datetime.timedelta(days=12)
        highlight_date_to = datetime.date.today() - datetime.timedelta(days=10)
        availability_date_from = datetime.date.today() - datetime.timedelta(days=10)
        availability_date_to = datetime.date.today() - datetime.timedelta(days=8)
        separator = " - "

        image_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(image_path, "rb") as image_file:
            response = self.post_to_endpoint(
                authenticated_client,
                form={
                    "name": name,
                    "description": description,
                    "availability_timespan": f"{availability_date_from.strftime('%d/%m/%Y')}{separator}{availability_date_to.strftime('%d/%m/%Y')}",
                    "highlight_timespan": f"{highlight_date_from.strftime('%d/%m/%Y')}{separator}{highlight_date_to.strftime('%d/%m/%Y')}",
                    "image": image_file,
                },
                expected_num_queries=self.expected_num_queries - 1,
            )
            assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == "Les données envoyées comportent des erreurs. Dates de diffusion sur l'espace partenaire : "
            "La date de fin de diffusion sur l'espace partenaire ne peut pas être dans le passé ; "
            "Dates de l'évènement : La date de fin de l'évènement ne peut pas être dans le passé ;"
        )

    def test_create_highlight_missing_field_should_fail(self, authenticated_client):
        response = self.post_to_endpoint(
            authenticated_client, form={}, expected_num_queries=self.expected_num_queries - 1
        )
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == "Les données envoyées comportent des erreurs. Nom de la valorisation thématique : Le nom est obligatoire ; "
            "Description : La description est obligatoire ; Dates de diffusion sur l'espace partenaire : "
            "Les dates de diffusion sur l'espace partenaire sont obligatoires ; Dates de l'évènement : "
            "Les dates de l'évènement sont obligatoires ; Image de la valorisation thématique (max. 1 Mo) : "
            "L'image de la valorisation thématique est obligatoire ;"
        )


class GetUpdateHighlightFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.highlights.get_update_highlight_form"
    endpoint_kwargs = {"highlight_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_HIGHLIGHT

    # session + current user
    # get highlight
    expected_num_queries = 3

    def test_get_update_highlight_form(self, authenticated_client):
        highlight = highlights_factories.HighlightFactory.create()
        highlight_id = highlight.id
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, highlight_id=highlight_id))
            assert response.status_code == 200


class UpdateHighlightTest(PostEndpointHelper):
    endpoint = "backoffice_web.highlights.update_highlight"
    endpoint_kwargs = {"highlight_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_HIGHLIGHT

    # - authenticated user
    # - user session
    # - get highlight
    # - insert update highlight or rollback
    expected_num_queries = 4

    def test_update_highlight(self, authenticated_client):
        highlight = highlights_factories.HighlightFactory.create()
        highlight_id = highlight.id

        new_name = "New name"
        new_description = "New description"
        new_image_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        new_highlight_date_from = datetime.date.today() + datetime.timedelta(days=11)
        new_highlight_date_to = datetime.date.today() + datetime.timedelta(days=12)
        new_availability_date_from = datetime.date.today() - datetime.timedelta(days=10)
        new_availability_date_to = datetime.date.today() + datetime.timedelta(days=10)
        separator = " - "
        with open(new_image_path, "rb") as image_file:
            response = self.post_to_endpoint(
                authenticated_client,
                highlight_id=highlight_id,
                form={
                    "name": new_name,
                    "description": new_description,
                    "availability_timespan": f"{new_availability_date_from.strftime('%d/%m/%Y')}{separator}{new_availability_date_to.strftime('%d/%m/%Y')}",
                    "highlight_timespan": f"{new_highlight_date_from.strftime('%d/%m/%Y')}{separator}{new_highlight_date_to.strftime('%d/%m/%Y')}",
                    "image": image_file,
                },
                expected_num_queries=self.expected_num_queries,
            )
            assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert html_parser.extract_alert(response.data) == f"La valorisation thématique {new_name} a été mise à jour"
        highlight = db.session.query(highlights_models.Highlight).one()
        assert highlight.name == new_name
        assert highlight.description == new_description
        assert highlight.availability_timespan.lower == datetime.datetime.combine(
            new_availability_date_from, datetime.time(0, 0, 0)
        )
        assert highlight.availability_timespan.upper == datetime.datetime.combine(
            new_availability_date_to, datetime.time(0, 0, 0)
        )
        assert highlight.highlight_timespan.lower == datetime.datetime.combine(
            new_highlight_date_from, datetime.time(0, 0, 0)
        )
        assert highlight.highlight_timespan.upper == datetime.datetime.combine(
            new_highlight_date_to, datetime.time(0, 0, 0)
        )

    def test_update_highlight_available_after_highlight(self, authenticated_client):
        highlight = highlights_factories.HighlightFactory.create()
        highlight_id = highlight.id

        availability_date_to = highlight.highlight_timespan.upper + datetime.timedelta(days=1)
        separator = " - "

        response = self.post_to_endpoint(
            authenticated_client,
            highlight_id=highlight_id,
            form={
                "name": highlight.name,
                "description": highlight.description,
                "availability_timespan": f"{highlight.availability_timespan.lower.strftime('%d/%m/%Y')}{separator}{availability_date_to.strftime('%d/%m/%Y')}",
                "highlight_timespan": f"{highlight.highlight_timespan.lower.strftime('%d/%m/%Y')}{separator}{highlight.highlight_timespan.upper.strftime('%d/%m/%Y')}",
            },
            expected_num_queries=self.expected_num_queries - 1,
        )
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == "La diffusion sur l'espace partenaire ne peut pas se terminer après la fin de l'évènement"
        )

    def test_update_highlight_in_the_past(self, authenticated_client):
        highlight = highlights_factories.HighlightFactory.create()
        highlight_id = highlight.id
        highlight_date_from = datetime.date.today() - datetime.timedelta(days=12)
        highlight_date_to = datetime.date.today() - datetime.timedelta(days=10)
        availability_date_from = datetime.date.today() - datetime.timedelta(days=10)
        availability_date_to = datetime.date.today() - datetime.timedelta(days=8)
        separator = " - "

        response = self.post_to_endpoint(
            authenticated_client,
            highlight_id=highlight_id,
            form={
                "name": highlight.name,
                "description": highlight.description,
                "availability_timespan": f"{availability_date_from.strftime('%d/%m/%Y')}{separator}{availability_date_to.strftime('%d/%m/%Y')}",
                "highlight_timespan": f"{highlight_date_from.strftime('%d/%m/%Y')}{separator}{highlight_date_to.strftime('%d/%m/%Y')}",
            },
            expected_num_queries=self.expected_num_queries - 1,
        )
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == "Les données envoyées comportent des erreurs. Dates de diffusion sur l'espace partenaire : "
            "La date de fin de diffusion sur l'espace partenaire ne peut pas être dans le passé ; "
            "Dates de l'évènement : La date de fin de l'évènement ne peut pas être dans le passé ;"
        )

    def test_update_highlight_missing_field_should_fail(self, authenticated_client):
        highlight = highlights_factories.HighlightFactory.create()
        highlight_id = highlight.id
        response = self.post_to_endpoint(
            authenticated_client, highlight_id=highlight_id, form={}, expected_num_queries=self.expected_num_queries - 1
        )
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == "Les données envoyées comportent des erreurs. Nom de la valorisation thématique : Le nom est obligatoire ; "
            "Description : La description est obligatoire ; Dates de diffusion sur l'espace partenaire : "
            "Les dates de diffusion sur l'espace partenaire sont obligatoires ; "
            "Dates de l'évènement : Les dates de l'évènement sont obligatoires ;"
        )
