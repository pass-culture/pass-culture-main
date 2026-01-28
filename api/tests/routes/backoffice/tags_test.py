from datetime import date
from datetime import timedelta

import pytest
from flask import url_for

from pcapi.core.criteria import constants
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.criteria import models as criteria_models
from pcapi.core.highlights import factories as highlight_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.utils import date as date_utils

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class CreateTagTest(PostEndpointHelper):
    endpoint = "backoffice_web.tags.create_tag"
    needed_permission = perm_models.Permissions.READ_TAGS

    def test_create_tag(self, authenticated_client):
        form = {"name": "my-tag", "description": "description"}

        response = self.post_to_endpoint(authenticated_client, form=form, follow_redirects=True)

        assert response.status_code == 200  # after redirect
        assert html_parser.extract_alert(response.data) == "Le nouveau tag offres et partenaires culturels a été créé"

        tag = db.session.query(criteria_models.Criterion).first()

        assert tag.name == "my-tag"
        assert tag.description == "description"
        assert not tag.startDateTime
        assert not tag.endDateTime

    def test_create_tag_with_categories(self, authenticated_client):
        category = criteria_factories.CriterionCategoryFactory()
        form = {"name": "my-tag", "description": "description", "categories": [category.id]}

        response = self.post_to_endpoint(authenticated_client, form=form, follow_redirects=True)

        assert response.status_code == 200  # after redirect
        assert html_parser.extract_alert(response.data) == "Le nouveau tag offres et partenaires culturels a été créé"

        tag = db.session.query(criteria_models.Criterion).one()

        assert tag.name == "my-tag"
        assert tag.description == "description"
        assert not tag.startDateTime
        assert not tag.endDateTime
        assert len(tag.categories) == 1
        assert tag.categories[0].label == category.label

    @pytest.mark.parametrize(
        "with_highlight_category,with_highglight,should_fail,alert_msg",
        [
            (True, True, False, "Le nouveau tag offres et partenaires culturels a été créé"),
            (
                True,
                False,
                True,
                f"Les données envoyées comportent des erreurs. Valorisation thématique : "
                f"La sélection d'une valorisation thématique est obligatoire pour les tags de la catégorie {constants.HIGHLIGHT_CATEGORY_LABEL} ;",
            ),
            (False, False, False, "Le nouveau tag offres et partenaires culturels a été créé"),
            (
                False,
                True,
                True,
                f"Les données envoyées comportent des erreurs. Valorisation thématique : "
                f"La sélection d'une valorisation thématique est impossible pour les tags qui ne sont pas dans la catégorie {constants.HIGHLIGHT_CATEGORY_LABEL} ;",
            ),
        ],
    )
    def test_create_tag_with_highlight_category(
        self, with_highlight_category, with_highglight, should_fail, alert_msg, authenticated_client
    ):
        if with_highlight_category:
            category = criteria_factories.CriterionCategoryFactory(label=constants.HIGHLIGHT_CATEGORY_LABEL)
        else:
            category = criteria_factories.CriterionCategoryFactory()
        if with_highglight:
            highlight = highlight_factories.HighlightFactory()
            form = {
                "name": "my-tag",
                "description": "description",
                "categories": [category.id],
                "highlight": highlight.id,
            }
        else:
            highlight = None
            form = {"name": "my-tag", "description": "description", "categories": [category.id]}

        response = self.post_to_endpoint(authenticated_client, form=form, follow_redirects=True)

        assert response.status_code == 200  # after redirect
        assert html_parser.extract_alert(response.data) == alert_msg

        tag = db.session.query(criteria_models.Criterion).first()
        if should_fail:
            assert tag is None
        else:
            assert tag.name == "my-tag"
            assert tag.description == "description"
            assert not tag.startDateTime
            assert not tag.endDateTime
            assert len(tag.categories) == 1
            assert tag.categories[0].label == category.label
            assert tag.highlight == highlight


class DeleteTagTest(PostEndpointHelper):
    endpoint = "backoffice_web.tags.delete_tag"
    endpoint_kwargs = {"tag_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_TAGS_N2

    def test_delete_tag(self, authenticated_client):
        offer = offers_factories.OfferFactory()
        tag = criteria_factories.CriterionFactory()
        offer.criteria = [tag]

        response = self.post_to_endpoint(authenticated_client, tag_id=tag.id)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.tags.list_tags")

        assert db.session.query(criteria_models.Criterion).count() == 0


class UpdateTagTest(PostEndpointHelper):
    endpoint = "backoffice_web.tags.update_tag"
    endpoint_kwargs = {"tag_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS

    @pytest.mark.parametrize(
        "with_highlight_category,with_highglight,should_fail,alert_msg",
        [
            (True, True, False, "Informations mises à jour"),
            (
                True,
                False,
                True,
                f"Les données envoyées comportent des erreurs. Valorisation thématique : "
                f"La sélection d'une valorisation thématique est obligatoire pour les tags de la catégorie {constants.HIGHLIGHT_CATEGORY_LABEL} ;",
            ),
            (False, False, False, "Informations mises à jour"),
            (
                False,
                True,
                True,
                f"Les données envoyées comportent des erreurs. Valorisation thématique : "
                f"La sélection d'une valorisation thématique est impossible pour les tags qui ne sont pas dans la catégorie {constants.HIGHLIGHT_CATEGORY_LABEL} ;",
            ),
        ],
    )
    def test_update_tag(self, with_highlight_category, with_highglight, should_fail, alert_msg, authenticated_client):
        if with_highlight_category:
            category1 = criteria_factories.CriterionCategoryFactory(label=constants.HIGHLIGHT_CATEGORY_LABEL)
            category2 = criteria_factories.CriterionCategoryFactory()
            categories = [category1, category2]
        else:
            categories = criteria_factories.CriterionCategoryFactory.create_batch(2)
        tag = criteria_factories.CriterionFactory(description="desc", startDateTime=None, endDateTime=None)

        new_tag_name = f"{tag.name}-update"
        new_tag_description = f"{tag.description} update"
        new_start_date = date.today()
        new_end_date = new_start_date + timedelta(days=1)

        if with_highglight:
            highlight = highlight_factories.HighlightFactory()
            form = {
                "name": new_tag_name,
                "description": new_tag_description,
                "start_date": new_start_date,
                "end_date": new_end_date,
                "categories": [category.id for category in categories],
                "highlight": highlight.id,
            }
        else:
            highlight = None
            form = {
                "name": new_tag_name,
                "description": new_tag_description,
                "start_date": new_start_date,
                "end_date": new_end_date,
                "categories": [category.id for category in categories],
            }

        response = self.post_to_endpoint(authenticated_client, tag_id=tag.id, form=form, follow_redirects=True)

        assert response.status_code == 200  # after redirect
        assert html_parser.extract_alert(response.data) == alert_msg

        db.session.refresh(tag)

        if should_fail:
            assert tag.name != new_tag_name
            assert tag.description != new_tag_description
            assert tag.startDateTime is None
            assert tag.endDateTime is None
            assert len(tag.categories) == 0
        else:
            assert tag.name == new_tag_name
            assert tag.description == new_tag_description
            assert tag.startDateTime.date() == new_start_date
            assert tag.endDateTime.date() == new_end_date
            assert len(tag.categories) == 2
            assert set(tag.categories) == set(categories)
            assert tag.highlight == highlight


class ListTagsTest(GetEndpointHelper):
    endpoint = "backoffice_web.tags.list_tags"
    endpoint_kwargs = {"tag_id": 1}
    needed_permission = perm_models.Permissions.READ_TAGS

    # - fetch session and user (1 query)
    # - fetch tags: rows and count (2 queries)
    # - fetch categories (1 query)
    expected_num_queries = 4

    def test_list_tags(self, authenticated_client):
        categories = criteria_factories.CriterionCategoryFactory.create_batch(2)

        now = date_utils.get_naive_utc_now()
        tag_1 = criteria_factories.CriterionFactory(
            description="tag1 description", startDateTime=now, categories=[categories[0]]
        )
        tag_2 = criteria_factories.CriterionFactory(
            description="tag2 description", startDateTime=now, categories=[categories[1]]
        )

        offers_factories.OfferFactory(criteria=[tag_1, tag_2])

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data, parent_class="tags-tab-pane")

        assert rows[0]["Nom"] == tag_1.name
        assert rows[0]["Description"] == tag_1.description
        assert rows[0]["Catégories"] == categories[0].label
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
    def test_search_list_tags(self, authenticated_client, q, expected_nb_results, expected_results_key):
        tags = {
            "tag1": criteria_factories.CriterionFactory(
                name="tag-1", description="tag1 description", startDateTime=date_utils.get_naive_utc_now()
            ),
            "tag2": criteria_factories.CriterionFactory(
                name="tag-2", description="tag2 description", startDateTime=date_utils.get_naive_utc_now()
            ),
        }

        offers_factories.OfferFactory(criteria=[tags["tag1"], tags["tag2"]])

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=q))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data, parent_class="tags-tab-pane")
        assert len(rows) == expected_nb_results
        count = 0
        for index, key in enumerate(expected_results_key):
            for row in rows:
                if count < expected_nb_results and row["Nom"] == tags.get(key).name:
                    assert rows[index]["Description"] == tags.get(key).description
                    count += 1
                    break

    @pytest.mark.parametrize(
        "total_items, pagination_config, expected_total_pages, expected_page, expected_items",
        (
            (31, {"per_page": 10}, 4, 1, 10),
            (31, {"per_page": 10, "page": 1}, 4, 1, 10),
            (31, {"per_page": 10, "page": 3}, 4, 3, 10),
            (31, {"per_page": 10, "page": 4}, 4, 4, 1),
            (20, {"per_page": 10, "page": 1}, 2, 1, 10),
            (27, {"page": 1}, 1, 1, 27),
            (10, {"per_page": 25, "page": 1}, 1, 1, 10),
            (1, {"per_page": None, "page": 1}, 1, 1, 1),
            (1, {"per_page": "", "page": 1}, 1, 1, 1),  # ensure that it does not crash (fallbacks to default)
        ),
    )
    def test_list_pagination(
        self, authenticated_client, total_items, pagination_config, expected_total_pages, expected_page, expected_items
    ):
        criteria_factories.CriterionFactory.create_batch(total_items)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **pagination_config))
            assert response.status_code == 200

        assert html_parser.count_table_rows(response.data) == expected_items
        assert html_parser.extract_pagination_info(response.data) == (
            expected_page,
            expected_total_pages,
            total_items,
        )


class CreateTagButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_OFFERS_AND_VENUES_TAGS
    button_label = "Créer un tag offres et partenaires culturels"

    @property
    def path(self):
        return url_for("backoffice_web.tags.list_tags")


class CreateTagCategoryButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_TAGS_N2
    button_label = "Créer une catégorie"

    @property
    def path(self):
        return url_for("backoffice_web.tags.list_tags")


class CreateTagCategoryTest(PostEndpointHelper):
    endpoint = "backoffice_web.tags.create_tag_category"
    needed_permission = perm_models.Permissions.MANAGE_TAGS_N2

    def test_create_tag_category(self, authenticated_client):
        form_data = {
            "label": "Nouvelle catégorie",
        }
        response = self.post_to_endpoint(authenticated_client, form=form_data)

        assert response.status_code == 303
        assert response.location == url_for("backoffice_web.tags.list_tags", active_tab="categories")

        assert db.session.query(criteria_models.CriterionCategory).filter_by(label=form_data["label"]).one_or_none()

    def test_create_with_already_existing_category(self, authenticated_client):
        criteria_factories.CriterionCategoryFactory(label="Duplicate")
        response = self.post_to_endpoint(authenticated_client, form={"label": "Duplicate"})

        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data) == "Cette catégorie existe déjà"
        )
