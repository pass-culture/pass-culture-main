import datetime

from flask import url_for
import pytest

from pcapi.core.chronicles import factories as chronicles_factories
from pcapi.core.history import models as history_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.models import db

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class ListChroniclesTest(GetEndpointHelper):
    endpoint = "backoffice_web.chronicles.list_chronicles"
    needed_permission = perm_models.Permissions.READ_CHRONICLE
    # session
    # current user
    # FF WIP_BO_CHRONICLES
    # list chronicles
    # count chronicles
    expected_num_queries = 5

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_without_filters(self, authenticated_client):
        product = offers_factories.ProductFactory()
        chronicle_with_product = chronicles_factories.ChronicleFactory(products=[product])
        chronicle_without_product = chronicles_factories.ChronicleFactory()
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert rows[0]["ID"] == str(chronicle_without_product.id)
        assert rows[0]["Titres des œuvres"] == ""
        assert rows[0]["Contenu"] == chronicle_without_product.content
        assert rows[0]["Date de création"] == chronicle_without_product.dateCreated.strftime("%d/%m/%Y")
        assert rows[1]["ID"] == str(chronicle_with_product.id)
        assert rows[1]["Titres des œuvres"] == product.name
        assert rows[1]["Contenu"] == chronicle_with_product.content
        assert rows[1]["Date de création"] == chronicle_with_product.dateCreated.strftime("%d/%m/%Y")

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_search_by_ean(self, authenticated_client):
        ean = "1234567890123"
        product = offers_factories.ProductFactory(extraData={"ean": ean})
        chronicle_with_product = chronicles_factories.ChronicleFactory(products=[product])
        chronicles_factories.ChronicleFactory()
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=ean))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(chronicle_with_product.id)

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_search_by_content(self, authenticated_client):
        chronicle_to_find = chronicles_factories.ChronicleFactory(
            content="Deux hommes, et même dix, peuvent bien en craindre un ;",
        )
        chronicles_factories.ChronicleFactory()
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    q="HomMe bien",
                    research_type="CHRONICLE_CONTENT",
                ),
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)

        assert len(rows) == 1
        assert rows[0]["ID"] == str(chronicle_to_find.id)

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_search_by_product_name(self, authenticated_client):
        product = offers_factories.ProductFactory(name="My super product")
        chronicle_with_product = chronicles_factories.ChronicleFactory(products=[product])
        chronicles_factories.ChronicleFactory()
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    q="SUPER",
                    research_type="PRODUCT_NAME",
                ),
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(chronicle_with_product.id)

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_search_by_creation_date(self, authenticated_client):
        chronicle_to_find = chronicles_factories.ChronicleFactory()
        chronicles_factories.ChronicleFactory(dateCreated=datetime.date(1999, 12, 12))
        chronicles_factories.ChronicleFactory(dateCreated=datetime.date(2038, 1, 19))
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, date_range="01/01/2000 - 18/01/2038"),
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(chronicle_to_find.id)


class GetChronicleDetailsTest(GetEndpointHelper):
    endpoint = "backoffice_web.chronicles.details"
    endpoint_kwargs = {"chronicle_id": 1}
    needed_permission = perm_models.Permissions.READ_CHRONICLE
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - FF WIP_BO_CHRONICLES
    # - fetch chronicle and its products
    # - fetch chronicle's action history
    expected_num_queries = 5

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_nominal(self, authenticated_client):
        products = [
            offers_factories.ProductFactory(extraData={"ean": "1235467890123"}),
            offers_factories.ProductFactory(),
        ]
        user = users_factories.BeneficiaryGrant18Factory()
        chronicle = chronicles_factories.ChronicleFactory(
            products=products,
            age=18,
            city="valechat",
            content="A short content",
            ean=products[0].extraData["ean"],
            email=user.email,
            firstName=user.firstName,
            isIdentityDiffusible=True,
            isSocialMediaDiffusible=True,
            user=user,
            isActive=True,
        )
        url = url_for(self.endpoint, chronicle_id=chronicle.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content_as_text = html_parser.content_as_text(response.data)

        assert f"Chronique de {chronicle.firstName}, {chronicle.age} ans"
        assert "Publié" in content_as_text
        assert f"Prénom : {chronicle.firstName} (Voir le profil du jeune)" in content_as_text
        assert f"Âge : {chronicle.age} ans" in content_as_text
        assert f"Ville : {chronicle.city}" in content_as_text
        assert f"Email : {chronicle.email}" in content_as_text
        assert f"Titre de l'œuvre : {products[0].name}" in content_as_text
        assert f"EAN : {chronicle.ean}" in content_as_text
        assert "Accord diffusion réseaux sociaux : Oui" in content_as_text
        assert "Accord de diffusion maison d'édition : Oui" in content_as_text
        assert chronicle.content in content_as_text

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_mininal(self, authenticated_client):

        chronicle = chronicles_factories.ChronicleFactory(isActive=False)
        url = url_for(self.endpoint, chronicle_id=chronicle.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content_as_text = html_parser.content_as_text(response.data)

        assert "Non publié" in content_as_text
        assert "Prénom : Non renseigné" in content_as_text
        assert "(Voir le profil du jeune)" not in content_as_text
        assert "Âge : Non renseigné" in content_as_text
        assert "Ville : Non renseignée" in content_as_text
        assert f"Email : {chronicle.email}" in content_as_text
        assert "Titre de l'œuvre : Non renseigné" in content_as_text
        assert "EAN : Non renseigné" in content_as_text
        assert "Accord diffusion réseaux sociaux : Non" in content_as_text
        assert "Accord de diffusion maison d'édition : Non" in content_as_text
        assert chronicle.content in content_as_text


class UpdateChronicleContentTest(PostEndpointHelper):
    endpoint = "backoffice_web.chronicles.update_chronicle_content"
    endpoint_kwargs = {"chronicle_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_CHRONICLE
    # session
    # current user
    # FF WIP_BO_CHRONICLES
    # get chronicle
    # update chronicle
    # GetChronicleDetailsTest.expected_num_queries (follow redirect)
    expected_num_queries = 5 + GetChronicleDetailsTest.expected_num_queries

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_update_chronicle_content(self, authenticated_client, legit_user):
        chronicle = chronicles_factories.ChronicleFactory(content="some old content")

        response = self.post_to_endpoint(
            follow_redirects=True,
            expected_num_queries=self.expected_num_queries,
            chronicle_id=chronicle.id,
            client=authenticated_client,
            form={"content": "new content"},
        )
        db.session.refresh(chronicle)

        content_as_text = html_parser.content_as_text(response.data)
        assert "new content" in content_as_text
        assert chronicle.content == "new content"
        assert html_parser.extract_alerts(response.data) == ["Le texte de la chronique a été mis à jour"]


class PublishChronicleTest(PostEndpointHelper):
    endpoint = "backoffice_web.chronicles.publish_chronicle"
    endpoint_kwargs = {"chronicle_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_CHRONICLE
    # session
    # current user
    # FF WIP_BO_CHRONICLES
    # get chronicle
    # update chronicle
    # reload chronicle
    # ListChroniclesTest.expected_num_queries (follow redirect)
    expected_num_queries = 6 + ListChroniclesTest.expected_num_queries

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_publish_chronicle(self, authenticated_client, legit_user):
        chronicle = chronicles_factories.ChronicleFactory(
            isActive=False,
        )

        response = self.post_to_endpoint(
            follow_redirects=True,
            expected_num_queries=self.expected_num_queries,
            chronicle_id=chronicle.id,
            client=authenticated_client,
        )
        db.session.refresh(chronicle)

        assert response.status_code == 200
        assert chronicle.isActive
        action_log = history_models.ActionHistory.query.one()
        assert action_log.actionType == history_models.ActionType.CHRONICLE_PUBLISHED
        assert action_log.chronicle is chronicle
        assert action_log.authorUser is legit_user

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_publish_chronicle_does_not_exist(self, authenticated_client):
        response = self.post_to_endpoint(
            follow_redirects=True,
            expected_num_queries=self.expected_num_queries - (1 + ListChroniclesTest.expected_num_queries),
            chronicle_id=0,
            client=authenticated_client,
        )
        assert response.status_code == 404


class UnpublishChronicleTest(PostEndpointHelper):
    endpoint = "backoffice_web.chronicles.unpublish_chronicle"
    endpoint_kwargs = {"chronicle_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_CHRONICLE
    # session
    # current user
    # FF WIP_BO_CHRONICLES
    # get chronicle
    # update chronicle
    # reload chronicle
    # ListChroniclesTest.expected_num_queries (follow redirect)
    expected_num_queries = 6 + ListChroniclesTest.expected_num_queries

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_unpublish_chronicle(self, authenticated_client, legit_user):
        chronicle = chronicles_factories.ChronicleFactory(
            isActive=True,
        )

        response = self.post_to_endpoint(
            follow_redirects=True,
            expected_num_queries=self.expected_num_queries,
            chronicle_id=chronicle.id,
            client=authenticated_client,
        )
        db.session.refresh(chronicle)

        assert response.status_code == 200
        assert not chronicle.isActive
        action_log = history_models.ActionHistory.query.one()
        assert action_log.actionType == history_models.ActionType.CHRONICLE_UNPUBLISHED
        assert action_log.chronicle is chronicle
        assert action_log.authorUser is legit_user

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_unpublish_chronicle_does_not_exist(self, authenticated_client):
        response = self.post_to_endpoint(
            follow_redirects=True,
            expected_num_queries=self.expected_num_queries - (1 + ListChroniclesTest.expected_num_queries),
            chronicle_id=0,
            client=authenticated_client,
        )
        assert response.status_code == 404


class AttachProductTest(PostEndpointHelper):
    endpoint = "backoffice_web.chronicles.attach_product"
    endpoint_kwargs = {"chronicle_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_CHRONICLE
    # session
    # current user
    # FF WIP_BO_CHRONICLES
    # get chronicle
    # get product
    # check if the chronicle is not already attached to the product
    # attach product to chronicle
    # GetChronicleDetailsTest.expected_num_queries (follow redirect)
    expected_num_queries = 7 + GetChronicleDetailsTest.expected_num_queries

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_attach_product(self, authenticated_client, legit_user):
        ean = "1234567890123"
        product = offers_factories.ProductFactory(extraData={"ean": ean})
        chronicle = chronicles_factories.ChronicleFactory()

        response = self.post_to_endpoint(
            follow_redirects=True,
            expected_num_queries=self.expected_num_queries,
            chronicle_id=chronicle.id,
            client=authenticated_client,
            form={"ean": ean},
        )
        db.session.refresh(chronicle)

        content_as_text = html_parser.content_as_text(response.data)
        assert product.name in content_as_text
        assert chronicle.products == [product]
        assert html_parser.extract_alerts(response.data) == [f"Le produit {product.name} a été rattaché à la chronique"]

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_product_not_found(self, authenticated_client, legit_user):
        chronicle = chronicles_factories.ChronicleFactory()

        response = self.post_to_endpoint(
            follow_redirects=True, chronicle_id=chronicle.id, client=authenticated_client, form={"ean": "1234567890123"}
        )
        db.session.refresh(chronicle)

        assert html_parser.extract_alerts(response.data) == ["Aucune œuvre n'a été trouvée pour cet EAN"]


class DetachProductTest(PostEndpointHelper):
    endpoint = "backoffice_web.chronicles.detach_product"
    endpoint_kwargs = {"chronicle_id": 1, "product_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_CHRONICLE
    # session
    # current user
    # FF WIP_BO_CHRONICLES
    # delete link between the chronicle and the product
    # GetChronicleDetailsTest.expected_num_queries (follow redirect)
    expected_num_queries = 4 + GetChronicleDetailsTest.expected_num_queries

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_detach_product(self, authenticated_client, legit_user):
        product = offers_factories.ProductFactory()
        chronicle = chronicles_factories.ChronicleFactory(products=[product])

        response = self.post_to_endpoint(
            follow_redirects=True,
            expected_num_queries=self.expected_num_queries,
            chronicle_id=chronicle.id,
            product_id=product.id,
            client=authenticated_client,
        )
        db.session.refresh(chronicle)

        content_as_text = html_parser.content_as_text(response.data)
        assert product.name not in content_as_text
        assert chronicle.products == []
        assert html_parser.extract_alerts(response.data) == ["Le produit à bien été détaché de la chronique"]

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_detach_unattached_product(self, authenticated_client, legit_user):
        product = offers_factories.ProductFactory()
        chronicle = chronicles_factories.ChronicleFactory()

        response = self.post_to_endpoint(
            follow_redirects=True,
            expected_num_queries=self.expected_num_queries + 1,  # rollback on error
            chronicle_id=chronicle.id,
            product_id=product.id,
            client=authenticated_client,
        )
        db.session.refresh(chronicle)

        assert chronicle.products == []
        assert html_parser.extract_alerts(response.data) == [
            "Le produit n'existe pas ou n'était pas attaché à la chronique"
        ]


class CommentChronicleTest(PostEndpointHelper):
    endpoint = "backoffice_web.chronicles.comment_chronicle"
    endpoint_kwargs = {"chronicle_id": 1}
    needed_permission = perm_models.Permissions.READ_CHRONICLE
    # session
    # current user
    # FF WIP_BO_CHRONICLES
    # get chronicle
    # insert actionHistory
    # GetChronicleDetailsTest.expected_num_queries (follow redirect)
    expected_num_queries = 5 + GetChronicleDetailsTest.expected_num_queries

    @override_features(WIP_ENABLE_CHRONICLES_IN_BO=True)
    def test_comment_chronicle(self, authenticated_client, legit_user):
        comment = "A very serious and concerned comment about the chronicle"
        chronicle = chronicles_factories.ChronicleFactory()

        response = self.post_to_endpoint(
            follow_redirects=True,
            expected_num_queries=self.expected_num_queries,
            chronicle_id=chronicle.id,
            client=authenticated_client,
            form={"comment": comment},
        )

        content_as_text = html_parser.content_as_text(response.data)
        assert comment in content_as_text
        assert html_parser.extract_alerts(response.data) == ["Le commentaire a été enregistré"]
        action_log = history_models.ActionHistory.query.one()
        assert action_log.actionType == history_models.ActionType.COMMENT
        assert action_log.chronicle is chronicle
        assert action_log.comment == comment
