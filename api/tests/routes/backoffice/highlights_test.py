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
    # session + user
    # list highlights
    # count highlights
    expected_num_queries = 3

    def test_without_filters(self, authenticated_client):
        highlight_1 = highlights_factories.HighlightFactory()
        highlight_2 = highlights_factories.HighlightFactory()
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["ID"] == str(highlight_1.id)
        assert rows[0]["Nom"] == highlight_1.name
        assert rows[0]["Description"] == highlight_1.description
        assert (
            rows[0]["Diffusion espace partenaire"]
            == f"{highlight_1.availability_datespan.lower.strftime('%d/%m/%Y')} → {(highlight_1.availability_datespan.upper - datetime.timedelta(days=1)).strftime('%d/%m/%Y')}"
        )
        assert (
            rows[0]["Date(s) d'évènement"]
            == f"{highlight_1.highlight_datespan.lower.strftime('%d/%m/%Y')} → {(highlight_1.highlight_datespan.upper - datetime.timedelta(days=1)).strftime('%d/%m/%Y')}"
        )

        assert rows[1]["ID"] == str(highlight_2.id)
        assert rows[1]["Nom"] == highlight_2.name
        assert rows[1]["Description"] == highlight_2.description
        assert (
            rows[1]["Diffusion espace partenaire"]
            == f"{highlight_2.availability_datespan.lower.strftime('%d/%m/%Y')} → {(highlight_2.availability_datespan.upper - datetime.timedelta(days=1)).strftime('%d/%m/%Y')}"
        )
        assert (
            rows[1]["Date(s) d'évènement"]
            == f"{highlight_2.highlight_datespan.lower.strftime('%d/%m/%Y')} → {(highlight_2.highlight_datespan.upper - datetime.timedelta(days=1)).strftime('%d/%m/%Y')}"
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
    expected_num_queries = 1

    def test_get_create_highlight_form(self, authenticated_client):
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200


class CreateHighlightTest(PostEndpointHelper):
    endpoint = "backoffice_web.highlights.create_highlight"
    needed_permission = perm_models.Permissions.MANAGE_HIGHLIGHT

    # - session + user
    # - insert into highlight or rollback
    expected_num_queries = 2

    def test_create_highlight(self, authenticated_client):
        today = datetime.date.today()
        name = "New highlight"
        description = "Highlight description"
        highlight_date_from = today + datetime.timedelta(days=11)
        highlight_date_to = today + datetime.timedelta(days=11)
        availability_date_from = today - datetime.timedelta(days=10)
        availability_date_to = today + datetime.timedelta(days=10)
        communication_date = today + datetime.timedelta(days=11)
        separator = " - "

        image_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(image_path, "rb") as image_file:
            response = self.post_to_endpoint(
                authenticated_client,
                form={
                    "name": name,
                    "description": description,
                    "availability_datespan": f"{availability_date_from.strftime('%d/%m/%Y')}{separator}{availability_date_to.strftime('%d/%m/%Y')}",
                    "highlight_datespan": f"{highlight_date_from.strftime('%d/%m/%Y')}{separator}{highlight_date_to.strftime('%d/%m/%Y')}",
                    "communication_date": communication_date,
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
        assert highlight.availability_datespan.lower == availability_date_from
        assert highlight.availability_datespan.upper == availability_date_to + datetime.timedelta(days=1)
        assert highlight.highlight_datespan.lower == highlight_date_from
        assert highlight.highlight_datespan.upper == highlight_date_to + datetime.timedelta(days=1)
        assert highlight.communication_date == communication_date

    def test_create_highlight_available_after_highlight_should_fail(self, authenticated_client):
        today = datetime.date.today()
        name = "New highlight"
        description = "Highlight description"
        highlight_date_from = today + datetime.timedelta(days=1)
        highlight_date_to = today + datetime.timedelta(days=2)
        availability_date_from = today - datetime.timedelta(days=10)
        availability_date_to = today + datetime.timedelta(days=10)
        communication_date = today + datetime.timedelta(days=1)
        separator = " - "

        image_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(image_path, "rb") as image_file:
            response = self.post_to_endpoint(
                authenticated_client,
                form={
                    "name": name,
                    "description": description,
                    "availability_datespan": f"{availability_date_from.strftime('%d/%m/%Y')}{separator}{availability_date_to.strftime('%d/%m/%Y')}",
                    "highlight_datespan": f"{highlight_date_from.strftime('%d/%m/%Y')}{separator}{highlight_date_to.strftime('%d/%m/%Y')}",
                    "communication_date": communication_date,
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
        today = datetime.date.today()
        name = "New highlight"
        description = "Highlight description"
        highlight_date_from = today - datetime.timedelta(days=10)
        highlight_date_to = today - datetime.timedelta(days=8)
        availability_date_from = today - datetime.timedelta(days=12)
        availability_date_to = today - datetime.timedelta(days=10)
        communication_date = today - datetime.timedelta(days=10)
        separator = " - "

        image_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(image_path, "rb") as image_file:
            response = self.post_to_endpoint(
                authenticated_client,
                form={
                    "name": name,
                    "description": description,
                    "availability_datespan": f"{availability_date_from.strftime('%d/%m/%Y')}{separator}{availability_date_to.strftime('%d/%m/%Y')}",
                    "highlight_datespan": f"{highlight_date_from.strftime('%d/%m/%Y')}{separator}{highlight_date_to.strftime('%d/%m/%Y')}",
                    "communication_date": communication_date,
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
        assert highlight.availability_datespan.lower == availability_date_from
        assert highlight.availability_datespan.upper == availability_date_to + datetime.timedelta(days=1)
        assert highlight.highlight_datespan.lower == highlight_date_from
        assert highlight.highlight_datespan.upper == highlight_date_to + datetime.timedelta(days=1)
        assert highlight.communication_date == communication_date

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
            "Les dates de l'évènement sont obligatoires ; Date de mise en avant (envoi du mail aux acteurs culturels) : La date de mise en avant est obligatoire ; "
            "Image de la valorisation thématique (max. 3 Mo) : L'image de la valorisation thématique est obligatoire ;"
        )

    def test_create_highlight_name_too_long_should_fail(self, authenticated_client):
        today = datetime.date.today()
        name = "a" * 61
        description = "Highlight description"
        highlight_date_from = today + datetime.timedelta(days=11)
        highlight_date_to = today + datetime.timedelta(days=12)
        availability_date_from = today - datetime.timedelta(days=10)
        availability_date_to = today + datetime.timedelta(days=10)
        separator = " - "
        communication_date = today + datetime.timedelta(days=10)

        image_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(image_path, "rb") as image_file:
            response = self.post_to_endpoint(
                authenticated_client,
                form={
                    "name": name,
                    "description": description,
                    "availability_datespan": f"{availability_date_from.strftime('%d/%m/%Y')}{separator}{availability_date_to.strftime('%d/%m/%Y')}",
                    "highlight_datespan": f"{highlight_date_from.strftime('%d/%m/%Y')}{separator}{highlight_date_to.strftime('%d/%m/%Y')}",
                    "communication_date": communication_date,
                    "image": image_file,
                },
                expected_num_queries=self.expected_num_queries - 1,
            )
            assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == "Les données envoyées comportent des erreurs. Nom de la valorisation thématique : doit contenir moins de 60 caractères ;"
        )

    def test_create_highlight_communication_date_after_highlight_should_fail(self, authenticated_client):
        today = datetime.date.today()
        name = "Name"
        description = "Highlight description"
        highlight_date_from = today + datetime.timedelta(days=11)
        highlight_date_to = today + datetime.timedelta(days=12)
        availability_date_from = today - datetime.timedelta(days=10)
        availability_date_to = today + datetime.timedelta(days=10)
        separator = " - "
        communication_date = today + datetime.timedelta(days=13)

        image_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(image_path, "rb") as image_file:
            response = self.post_to_endpoint(
                authenticated_client,
                form={
                    "name": name,
                    "description": description,
                    "availability_datespan": f"{availability_date_from.strftime('%d/%m/%Y')}{separator}{availability_date_to.strftime('%d/%m/%Y')}",
                    "highlight_datespan": f"{highlight_date_from.strftime('%d/%m/%Y')}{separator}{highlight_date_to.strftime('%d/%m/%Y')}",
                    "communication_date": communication_date,
                    "image": image_file,
                },
                expected_num_queries=self.expected_num_queries - 1,
            )
            assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == "La date de mise en avant ne peut pas être après la fin de l'évènement"
        )

    @pytest.mark.parametrize(
        "file_path,max_image_size_value,min_width_image_value,error_msg",
        [
            (
                pathlib.Path(tests.__path__[0]) / "files" / "pdf" / "example.html",
                None,
                None,
                "Le fichier fourni n'est pas une image",
            ),
            (
                pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg",
                1_000,
                None,
                "Image trop grande, max : 0 Mo",
            ),
            (
                pathlib.Path(tests.__path__[0]) / "files" / "mouette_small.jpg",
                None,
                1_000_000,
                "Image trop petite, utilisez une image plus grande (supérieure à 270px par 1000000px)",
            ),
        ],
    )
    def test_create_highlight_image_should_fail(
        self,
        file_path,
        max_image_size_value,
        min_width_image_value,
        error_msg,
        mocker,
        authenticated_client,
    ):
        today = datetime.date.today()
        name = "New highlight"
        description = "Highlight description"
        highlight_date_from = today + datetime.timedelta(days=11)
        highlight_date_to = today + datetime.timedelta(days=11)
        availability_date_from = today - datetime.timedelta(days=10)
        availability_date_to = today + datetime.timedelta(days=10)
        communication_date = today + datetime.timedelta(days=11)
        separator = " - "

        if max_image_size_value:
            mocker.patch("pcapi.routes.backoffice.forms.fields.MAX_IMAGE_SIZE", max_image_size_value)
        if min_width_image_value:
            mocker.patch("pcapi.routes.backoffice.forms.fields.MIN_IMAGE_HEIGHT", min_width_image_value)

        image_path = file_path
        with open(image_path, "rb") as image_file:
            response = self.post_to_endpoint(
                authenticated_client,
                form={
                    "name": name,
                    "description": description,
                    "availability_datespan": f"{availability_date_from.strftime('%d/%m/%Y')}{separator}{availability_date_to.strftime('%d/%m/%Y')}",
                    "highlight_datespan": f"{highlight_date_from.strftime('%d/%m/%Y')}{separator}{highlight_date_to.strftime('%d/%m/%Y')}",
                    "communication_date": communication_date,
                    "image": image_file,
                },
                expected_num_queries=self.expected_num_queries - 1,
            )
            assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == f"Les données envoyées comportent des erreurs. Image de la valorisation thématique (max. 3 Mo) : {error_msg} ;"
        )


class GetUpdateHighlightFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.highlights.get_update_highlight_form"
    endpoint_kwargs = {"highlight_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_HIGHLIGHT

    # session + current user
    # get highlight
    expected_num_queries = 2

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

    # - session + user
    # - get highlight
    # - insert update highlight or rollback
    expected_num_queries = 3

    def test_update_highlight(self, authenticated_client):
        today = datetime.date.today()
        highlight = highlights_factories.HighlightFactory.create()
        highlight_id = highlight.id

        new_name = "New name"
        new_description = "New description"
        new_image_path = pathlib.Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        new_highlight_date_from = today + datetime.timedelta(days=11)
        new_highlight_date_to = today + datetime.timedelta(days=12)
        new_availability_date_from = today - datetime.timedelta(days=10)
        new_availability_date_to = today + datetime.timedelta(days=10)
        new_communication_date = today + datetime.timedelta(days=11)
        separator = " - "
        with open(new_image_path, "rb") as image_file:
            response = self.post_to_endpoint(
                authenticated_client,
                highlight_id=highlight_id,
                form={
                    "name": new_name,
                    "description": new_description,
                    "availability_datespan": f"{new_availability_date_from.strftime('%d/%m/%Y')}{separator}{new_availability_date_to.strftime('%d/%m/%Y')}",
                    "highlight_datespan": f"{new_highlight_date_from.strftime('%d/%m/%Y')}{separator}{new_highlight_date_to.strftime('%d/%m/%Y')}",
                    "communication_date": new_communication_date,
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
        assert highlight.availability_datespan.lower == new_availability_date_from
        assert highlight.availability_datespan.upper == new_availability_date_to + datetime.timedelta(days=1)
        assert highlight.highlight_datespan.lower == new_highlight_date_from
        assert highlight.highlight_datespan.upper == new_highlight_date_to + datetime.timedelta(days=1)

    def test_update_highlight_available_after_highlight_should_fail(self, authenticated_client):
        highlight = highlights_factories.HighlightFactory.create()
        highlight_id = highlight.id

        availability_date_to = highlight.highlight_datespan.upper + datetime.timedelta(days=1)
        separator = " - "

        response = self.post_to_endpoint(
            authenticated_client,
            highlight_id=highlight_id,
            form={
                "name": highlight.name,
                "description": highlight.description,
                "availability_datespan": f"{highlight.availability_datespan.lower.strftime('%d/%m/%Y')}{separator}{availability_date_to.strftime('%d/%m/%Y')}",
                "highlight_datespan": f"{highlight.highlight_datespan.lower.strftime('%d/%m/%Y')}{separator}{highlight.highlight_datespan.upper.strftime('%d/%m/%Y')}",
                "communication_date": highlight.communication_date,
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
        today = datetime.date.today()
        highlight = highlights_factories.HighlightFactory.create()
        highlight_id = highlight.id
        highlight_date_from = today - datetime.timedelta(days=10)
        highlight_date_to = today - datetime.timedelta(days=8)
        availability_date_from = today - datetime.timedelta(days=12)
        availability_date_to = today - datetime.timedelta(days=10)
        separator = " - "
        new_communication_date = today - datetime.timedelta(days=10)

        response = self.post_to_endpoint(
            authenticated_client,
            highlight_id=highlight_id,
            form={
                "name": highlight.name,
                "description": highlight.description,
                "availability_datespan": f"{availability_date_from.strftime('%d/%m/%Y')}{separator}{availability_date_to.strftime('%d/%m/%Y')}",
                "highlight_datespan": f"{highlight_date_from.strftime('%d/%m/%Y')}{separator}{highlight_date_to.strftime('%d/%m/%Y')}",
                "communication_date": new_communication_date,
            },
            expected_num_queries=self.expected_num_queries,
        )
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data) == f"La valorisation thématique {highlight.name} a été mise à jour"
        )
        highlight = db.session.query(highlights_models.Highlight).one()
        assert highlight.availability_datespan.lower == availability_date_from
        assert highlight.availability_datespan.upper == availability_date_to + datetime.timedelta(days=1)
        assert highlight.highlight_datespan.lower == highlight_date_from
        assert highlight.highlight_datespan.upper == highlight_date_to + datetime.timedelta(days=1)

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
            "Dates de l'évènement : Les dates de l'évènement sont obligatoires ; "
            "Date de mise en avant (envoi du mail aux acteurs culturels) : La date de mise en avant est obligatoire ;"
        )

    def test_update_highlight_name_too_long_should_fail(self, authenticated_client):
        highlight = highlights_factories.HighlightFactory.create()
        highlight_id = highlight.id
        new_name = "a" * 61

        separator = " - "

        response = self.post_to_endpoint(
            authenticated_client,
            highlight_id=highlight_id,
            form={
                "name": new_name,
                "description": highlight.description,
                "availability_datespan": f"{highlight.availability_datespan.lower.strftime('%d/%m/%Y')}{separator}{highlight.availability_datespan.upper.strftime('%d/%m/%Y')}",
                "highlight_datespan": f"{highlight.highlight_datespan.lower.strftime('%d/%m/%Y')}{separator}{highlight.highlight_datespan.upper.strftime('%d/%m/%Y')}",
                "communication_date": highlight.communication_date,
            },
            expected_num_queries=self.expected_num_queries - 1,
        )
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == "Les données envoyées comportent des erreurs. Nom de la valorisation thématique : doit contenir moins de 60 caractères ;"
        )

    def test_create_highlight_communication_date_after_highlight_should_fail(self, authenticated_client):
        highlight = highlights_factories.HighlightFactory.create()
        highlight_id = highlight.id
        new_communication_date = highlight.highlight_datespan.upper + datetime.timedelta(days=1)

        separator = " - "

        response = self.post_to_endpoint(
            authenticated_client,
            highlight_id=highlight_id,
            form={
                "name": highlight.name,
                "description": highlight.description,
                "availability_datespan": f"{highlight.availability_datespan.lower.strftime('%d/%m/%Y')}{separator}{highlight.availability_datespan.upper.strftime('%d/%m/%Y')}",
                "highlight_datespan": f"{highlight.highlight_datespan.lower.strftime('%d/%m/%Y')}{separator}{highlight.highlight_datespan.upper.strftime('%d/%m/%Y')}",
                "communication_date": new_communication_date,
            },
            expected_num_queries=self.expected_num_queries - 1,
        )
        assert response.status_code == 303

        response = authenticated_client.get(response.location)
        assert (
            html_parser.extract_alert(response.data)
            == "La date de mise en avant ne peut pas être après la fin de l'évènement"
        )
