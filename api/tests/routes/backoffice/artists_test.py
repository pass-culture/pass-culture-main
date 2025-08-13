from unittest.mock import patch

import pytest
from flask import url_for

from pcapi.core.artist import factories as artist_factories
from pcapi.core.artist import models as artist_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class GetArtistDetailsTest(GetEndpointHelper):
    endpoint = "backoffice_web.artist.get_artist_details"
    endpoint_kwargs = {"artist_id": "some-uuid"}
    needed_permission = perm_models.Permissions.READ_OFFERS

    # user + session + artist
    expected_num_queries = 3

    def test_get_artist_details_success(self, authenticated_client):
        product1 = offers_factories.ProductFactory.create()
        artist = artist_factories.ArtistFactory.create(description="A famous artist.", products=[product1])
        artist_factories.ArtistAliasFactory.create(artist=artist, artist_alias_name="Alias 1")

        url = url_for(self.endpoint, artist_id=artist.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)

        assert response.status_code == 200
        descriptions = html_parser.extract_descriptions(response.data)
        assert descriptions["Artist ID"] == artist.id
        assert "Alias 1" in descriptions["Alias"]


class EditArtistButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_OFFERS
    button_label = "Éditer"

    @property
    def path(self):
        artist = artist_factories.ArtistFactory.create()
        return url_for("backoffice_web.artist.get_artist_details", artist_id=artist.id)


class GetArtistEditFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.artist.get_artist_edit_form"
    endpoint_kwargs = {"artist_id": "some-uuid"}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    # user + session + artist
    expected_num_queries = 3

    def test_get_edit_form_success(self, authenticated_client):
        artist = artist_factories.ArtistFactory.create()
        url = url_for(self.endpoint, artist_id=artist.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert f"Éditer l'artiste {artist.name}" in response_text
        assert "Enregistrer" in response_text


class PostArtistEditTest(PostEndpointHelper):
    endpoint = "backoffice_web.artist.post_artist_edit_form"
    endpoint_kwargs = {"artist_id": "some-uuid"}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    def test_edit_artist_success(self, db_session, authenticated_client):
        artist = artist_factories.ArtistFactory.create(name="Old Name")
        form_data = {"name": "New Name", "description": "New Description"}

        response = self.post_to_endpoint(
            authenticated_client, artist_id=artist.id, form=form_data, follow_redirects=True
        )

        assert response.status_code == 200
        assert f"L'artiste {artist.name} a été mis à jour." in html_parser.extract_alerts(response.data)
        artist = db_session.query(artist_models.Artist).filter_by(id=artist.id).one()
        assert artist.name == "New Name"


class BlacklistArtistButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
    button_label = "Blacklister"

    @property
    def path(self):
        artist = artist_factories.ArtistFactory.create(is_blacklisted=False)
        return url_for("backoffice_web.artist.get_artist_details", artist_id=artist.id)


class GetArtistBlacklistFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.artist.get_artist_blacklist_form"
    endpoint_kwargs = {"artist_id": "some-uuid"}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    # user + session + artist
    expected_num_queries = 3

    def test_get_blacklist_form_success(self, authenticated_client):
        artist = artist_factories.ArtistFactory.create()
        url = url_for(self.endpoint, artist_id=artist.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        response_text = html_parser.content_as_text(response.data)
        assert f"Blacklister l'artiste {artist.name}" in response_text
        assert "Confirmer" in response_text


class PostArtistBlacklistTest(PostEndpointHelper):
    endpoint = "backoffice_web.artist.post_artist_blacklist"
    endpoint_kwargs = {"artist_id": "some-uuid"}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_blacklist_artist_success(self, db_session, authenticated_client):
        artist = artist_factories.ArtistFactory.create(is_blacklisted=False)
        with patch("pcapi.routes.backoffice.artists.blueprint.db.session.commit"):
            response = self.post_to_endpoint(authenticated_client, artist_id=artist.id, follow_redirects=True)
            assert response.status_code == 200

        artist = db.session.query(artist_models.Artist).filter_by(id=artist.id).one()
        assert artist.is_blacklisted is True
        assert f"L'artiste {artist.name} a été blacklisté." in html_parser.extract_alerts(response.data)


class UnblacklistArtistButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
    button_label = "Réactiver"

    @property
    def path(self):
        artist = artist_factories.ArtistFactory.create(is_blacklisted=True)
        return url_for("backoffice_web.artist.get_artist_details", artist_id=artist.id)


class GetArtistUnblacklistFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.artist.get_artist_unblacklist_form"
    endpoint_kwargs = {"artist_id": "some-uuid"}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    # user + session + artist
    expected_num_queries = 3

    def test_get_blacklist_form_success(self, authenticated_client):
        artist = artist_factories.ArtistFactory.create(is_blacklisted=True)
        url = url_for(self.endpoint, artist_id=artist.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)

        assert response.status_code == 200
        assert f"Réactiver l'artiste {artist.name}" in html_parser.content_as_text(response.data)
        assert "Confirmer" in html_parser.content_as_text(response.data)


class PostArtistUnblacklistTest(PostEndpointHelper):
    endpoint = "backoffice_web.artist.post_artist_unblacklist"
    endpoint_kwargs = {"artist_id": "some-uuid"}
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS

    def test_unblacklist_artist_success(self, db_session, authenticated_client):
        artist = artist_factories.ArtistFactory.create(is_blacklisted=True)
        response = self.post_to_endpoint(authenticated_client, artist_id=artist.id, follow_redirects=True)
        db_session.refresh(artist)
        assert response.status_code == 200
        assert f"L'artiste {artist.name} a été réactivé." in html_parser.extract_alerts(response.data)
        assert artist.is_blacklisted is False


class LinkProductButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_OFFERS
    button_label = "Associer un produit"

    @property
    def path(self):
        artist = artist_factories.ArtistFactory.create()
        return url_for("backoffice_web.artist.get_artist_details", artist_id=artist.id)


class GetAssociateProductFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.artist.associate_product_form"
    endpoint_kwargs = {"artist_id": "some-uuid"}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    # user + session + artist
    expected_num_queries = 3

    def test_get_associate_product_form(self, authenticated_client):
        artist = artist_factories.ArtistFactory.create()
        url = url_for(self.endpoint, artist_id=artist.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)

        assert response.status_code == 200
        assert "Associer un produit" in html_parser.content_as_text(response.data)
        assert (
            f"Rechercher un produit via son identifiant pour l'associer à {artist.name}"
            in html_parser.content_as_text(response.data)
        )


class PostConfirmAssociationTest(PostEndpointHelper):
    endpoint = "backoffice_web.artist.confirm_association"
    endpoint_kwargs = {"artist_id": "some-uuid"}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    def test_associate_product_success(self, db_session, authenticated_client):
        artist = artist_factories.ArtistFactory.create()
        product = offers_factories.ProductFactory.create()
        form_data = {"product_id": product.id, "artist_type": artist_models.ArtistType.AUTHOR.name}
        response = self.post_to_endpoint(authenticated_client, artist_id=artist.id, form=form_data)

        assert response.status_code == 303
        link = (
            db_session.query(artist_models.ArtistProductLink)
            .filter_by(artist_id=artist.id, product_id=product.id)
            .one()
        )
        assert link is not None
        assert link.artist_type == artist_models.ArtistType.AUTHOR

    def test_already_associtated_product(self, db_session, authenticated_client):
        artist = artist_factories.ArtistFactory.create()
        product = offers_factories.ProductFactory.create()
        artist_factories.ArtistProductLinkFactory.create(artist_id=artist.id, product_id=product.id)

        form_data = {"product_id": product.id, "artist_type": artist_models.ArtistType.AUTHOR.name}
        response = self.post_to_endpoint(
            authenticated_client, artist_id=artist.id, form=form_data, follow_redirects=True
        )

        assert response.status_code == 200
        assert "Ce produit est déjà associé à cet artiste." in html_parser.extract_alerts(response.data)


class GetUnlinkProductFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.artist.get_unlink_product_form"
    endpoint_kwargs = {"artist_id": "some-uuid", "product_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    # user + session + artist + product
    expected_num_queries = 4

    def test_get_unlink_form_success(self, authenticated_client):
        artist = artist_factories.ArtistFactory.create()
        product = offers_factories.ProductFactory.create()
        url = url_for(self.endpoint, artist_id=artist.id, product_id=product.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)

        assert response.status_code == 200
        html_content = html_parser.content_as_text(response.data)
        assert "Dissocier un produit" in html_content
        assert (
            f"Êtes-vous sûr de vouloir supprimer le lien entre l'artiste {artist.name} et le produit {product.name} ?"
            in html_content
        )


class PostUnlinkProductTest(PostEndpointHelper):
    endpoint = "backoffice_web.artist.post_unlink_product"
    endpoint_kwargs = {"artist_id": "some-uuid", "product_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    def test_unlink_product_success(self, db_session, authenticated_client):
        product = offers_factories.ProductFactory.create()
        artist = artist_factories.ArtistFactory.create(products=[product])

        response = self.post_to_endpoint(
            authenticated_client, artist_id=artist.id, product_id=product.id, follow_redirects=True
        )
        assert response.status_code == 200
        assert response.data == b""

        link_exists = (
            db_session.query(artist_models.ArtistProductLink)
            .filter_by(artist_id=artist.id, product_id=product.id)
            .one_or_none()
        )
        assert link_exists is None


class MergeArtistButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_OFFERS
    button_label = "Fusionner"

    @property
    def path(self):
        artist = artist_factories.ArtistFactory.create()
        return url_for("backoffice_web.artist.get_artist_details", artist_id=artist.id)


class GetMergeArtistFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.artist.get_merge_artist_form"
    endpoint_kwargs = {"artist_id": "some-uuid"}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    # user + session + artist
    expected_num_queries = 3

    def test_get_merge_form_success(self, authenticated_client):
        artist = artist_factories.ArtistFactory.create()
        url = url_for(self.endpoint, artist_id=artist.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        html_content = html_parser.content_as_text(response.data)
        assert f"Fusionner l'artiste {artist.name}" in html_content
        assert (
            f"L'artiste {artist.name} sera conservé. Tous les produits et alias de l'artiste sélectionné seront transférés, puis cet artiste sera supprimé."
            in html_content
        )


class PostMergeArtistsTest(PostEndpointHelper):
    endpoint = "backoffice_web.artist.post_merge_artists"
    endpoint_kwargs = {"artist_id": "some-uuid"}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    def test_merge_artists_success(self, db_session, authenticated_client):
        artist_to_keep = artist_factories.ArtistFactory.create()
        product1 = offers_factories.ProductFactory.create()
        product2 = offers_factories.ProductFactory.create()
        artist_to_delete = artist_factories.ArtistFactory.create(products=[product1, product2])
        artist_to_delete_id = artist_to_delete.id

        alias1 = artist_factories.ArtistAliasFactory.create(artist=artist_to_delete)
        alias2 = artist_factories.ArtistAliasFactory.create(artist=artist_to_delete)

        response = self.post_to_endpoint(
            authenticated_client,
            artist_id=artist_to_keep.id,
            form={"target_artist_id": artist_to_delete_id},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert (
            f"L'artiste {artist_to_delete.name} a été fusionné avec succès dans {artist_to_keep.name}."
            in html_parser.extract_alerts(response.data)
        )
        deleted_artist_query = db_session.query(artist_models.Artist).filter_by(id=artist_to_delete_id).first()
        assert deleted_artist_query is None
        assert product1 in artist_to_keep.products
        assert product2 in artist_to_keep.products
        assert alias1 in artist_to_keep.aliases
        assert alias2 in artist_to_keep.aliases


class SplitArtistButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.MANAGE_OFFERS
    button_label = "Séparer"

    @property
    def path(self):
        artist = artist_factories.ArtistFactory.create()
        return url_for("backoffice_web.artist.get_artist_details", artist_id=artist.id)


class GetSplitArtistFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.artist.get_split_artist_form"
    endpoint_kwargs = {"artist_id": "some-uuid"}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    # user + session + artist
    expected_num_queries = 3

    def test_get_split_form_success(self, authenticated_client):
        product1 = offers_factories.ProductFactory.create()
        artist = artist_factories.ArtistFactory.create(products=[product1])

        url = url_for(self.endpoint, artist_id=artist.id)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)

        assert response.status_code == 200
        html_content = html_parser.content_as_text(response.data)
        assert f"Séparer l'artiste {artist.name}" in html_content
        assert "Nom du nouvel artiste" in html_content
        assert "Description du nouvel artiste" in html_content
        assert "Alias du nouvel artiste" in html_content
        assert "Produits à transférer au nouvel artiste" in html_content


class PostSplitArtistTest(PostEndpointHelper):
    endpoint = "backoffice_web.artist.post_split_artist"
    endpoint_kwargs = {"artist_id": "some-uuid"}
    needed_permission = perm_models.Permissions.MANAGE_OFFERS

    def test_split_artist_success(self, db_session, authenticated_client):
        product_to_move = offers_factories.ProductFactory.create()
        source_artist = artist_factories.ArtistFactory.create(products=[product_to_move])
        new_artist_name = "New Split Artist"

        form_data = {
            "new_artist_name": new_artist_name,
            "products_to_move": [product_to_move.id],
        }

        response = self.post_to_endpoint(
            authenticated_client, artist_id=source_artist.id, form=form_data, follow_redirects=True
        )
        assert response.status_code == 200
        assert (
            f'L\'artiste a été séparé avec succès. Le nouvel artiste "{new_artist_name}" a été créé.'
            in html_parser.extract_alerts(response.data)
        )

        new_artist = db_session.query(artist_models.Artist).filter_by(name="New Split Artist").one()
        assert product_to_move in new_artist.products
