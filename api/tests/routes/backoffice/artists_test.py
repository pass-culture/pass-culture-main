import datetime
from unittest.mock import patch

import pytest
from flask import url_for

from pcapi.core.artist import factories as artist_factories
from pcapi.core.artist import models as artist_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.search.models import IndexationReason
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


class GetArtistDetailsTest(GetEndpointHelper):
    endpoint = "backoffice_web.artist.get_artist_details"
    endpoint_kwargs = {"artist_id": "some-uuid"}
    needed_permission = perm_models.Permissions.READ_OFFERS

    # Expected queries:
    # 2. Session + user
    # 3. Artist with joinedload on products
    # 4. selectinload on aliases
    expected_num_queries = 3

    def test_get_artist_details_success(self, authenticated_client):
        product1 = offers_factories.ProductFactory.create()
        artist = artist_factories.ArtistFactory.create(
            description="A famous artist.",
            biography="Born in a small town.",
            wikidata_id="Q12345",
            wikipedia_url="https://fr.wikipedia.org/wiki/Artist",
            products=[product1],
        )
        artist_factories.ArtistAliasFactory.create(artist=artist, artist_alias_name="Alias 1")

        url = url_for(self.endpoint, artist_id=artist.id, _external=True)
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url)

        assert response.status_code == 200
        descriptions = html_parser.extract_descriptions(response.data)
        assert descriptions["Artist ID"] == artist.id
        assert "Alias 1" in descriptions["Alias"]
        assert "Born in a small town." in descriptions["Biographie Contenu généré par IA à partir de Wikipédia"]
        assert "Q12345" in descriptions["ID Wikidata"]
        assert "https://fr.wikipedia.org/wiki/Artist" in descriptions["URL Wikipédia"]


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

    # session + artist
    expected_num_queries = 2

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

    @patch("pcapi.routes.backoffice.artists.blueprint.async_index_artist_ids")
    def test_edit_artist_success(self, mock_async_index_artist_ids, db_session, authenticated_client):
        artist = artist_factories.ArtistFactory.create(
            name="Old Name",
            description="Old Desc",
            biography="Old Bio",
            wikidata_id="Q111",
            wikipedia_url="https://fr.wikipedia.org/wiki/Old_Url",
        )

        form_data = {
            "name": "New Name",
            "description": "New Description",
            "biography": "New Biography Content",
            "wikidata_id": "Q99999",
            "wikipedia_url": "https://fr.wikipedia.org/wiki/New_Url",
        }

        response = self.post_to_endpoint(
            authenticated_client, artist_id=artist.id, form=form_data, follow_redirects=True
        )

        assert response.status_code == 200
        mock_async_index_artist_ids.assert_called_once_with([artist.id], reason=IndexationReason.ARTIST_EDITION)
        assert f"L'artiste {artist.name} a été mis à jour." in html_parser.extract_alerts(response.data)
        artist = db_session.query(artist_models.Artist).filter_by(id=artist.id).one()
        assert artist.name == "New Name"
        assert artist.description == "New Description"
        assert artist.biography == "New Biography Content"
        assert artist.wikidata_id == "Q99999"
        assert artist.wikipedia_url == "https://fr.wikipedia.org/wiki/New_Url"


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

    # session + artist
    expected_num_queries = 2

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

    @patch("pcapi.routes.backoffice.artists.blueprint.async_index_artist_ids")
    @patch("pcapi.routes.backoffice.artists.blueprint.async_index_offers_of_artist_ids")
    def test_blacklist_artist_success(
        self, mock_async_index_offers_of_artist_ids, mock_async_index_artist_ids, db_session, authenticated_client
    ):
        artist = artist_factories.ArtistFactory.create(is_blacklisted=False)
        with patch("pcapi.routes.backoffice.artists.blueprint.db.session.commit"):
            response = self.post_to_endpoint(authenticated_client, artist_id=artist.id, follow_redirects=True)
            assert response.status_code == 200

        artist = db.session.query(artist_models.Artist).filter_by(id=artist.id).one()
        assert artist.is_blacklisted is True
        mock_async_index_artist_ids.assert_called_once_with([artist.id], reason=IndexationReason.ARTIST_BLACKLISTING)
        mock_async_index_offers_of_artist_ids.assert_called_once_with(
            [artist.id], reason=IndexationReason.ARTIST_BLACKLISTING
        )
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

    # session + artist
    expected_num_queries = 2

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

    @patch("pcapi.routes.backoffice.artists.blueprint.async_index_artist_ids")
    @patch("pcapi.routes.backoffice.artists.blueprint.async_index_offers_of_artist_ids")
    def test_unblacklist_artist_success(
        self, mock_async_index_offers_of_artist_ids, mock_async_index_artist_ids, db_session, authenticated_client
    ):
        artist = artist_factories.ArtistFactory.create(is_blacklisted=True)
        response = self.post_to_endpoint(authenticated_client, artist_id=artist.id, follow_redirects=True)
        db_session.refresh(artist)
        assert response.status_code == 200
        mock_async_index_artist_ids.assert_called_once_with([artist.id], reason=IndexationReason.ARTIST_UNBLACKLISTING)
        mock_async_index_offers_of_artist_ids.assert_called_once_with(
            [artist.id], reason=IndexationReason.ARTIST_UNBLACKLISTING
        )
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

    # session + artist
    expected_num_queries = 2

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

    @patch("pcapi.routes.backoffice.artists.blueprint.async_index_artist_ids")
    def test_associate_product_success(self, mock_async_index_artist_ids, db_session, authenticated_client):
        artist = artist_factories.ArtistFactory.create()
        product = offers_factories.ProductFactory.create()
        form_data = {"product_id": product.id, "artist_type": artist_models.ArtistType.AUTHOR.name}
        response = self.post_to_endpoint(authenticated_client, artist_id=artist.id, form=form_data)

        assert response.status_code == 303
        mock_async_index_artist_ids.assert_called_once_with([artist.id], reason=IndexationReason.ARTIST_LINKS_UPDATE)
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

    # session + artist + product
    expected_num_queries = 3

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

    @patch("pcapi.routes.backoffice.artists.blueprint.async_index_artist_ids")
    @patch("pcapi.routes.backoffice.artists.blueprint.async_index_offer_ids")
    def test_unlink_product_success(
        self, mock_async_index_offer_ids, mock_async_index_artist_ids, db_session, authenticated_client
    ):
        product = offers_factories.ProductFactory.create()
        offer = offers_factories.OfferFactory.create(product=product)
        artist = artist_factories.ArtistFactory.create(products=[product])

        response = self.post_to_endpoint(
            authenticated_client, artist_id=artist.id, product_id=product.id, follow_redirects=True
        )
        assert response.status_code == 200
        mock_async_index_artist_ids.assert_called_once_with([artist.id], reason=IndexationReason.ARTIST_LINKS_UPDATE)
        mock_async_index_offer_ids.assert_called_once_with([offer.id], reason=IndexationReason.ARTIST_LINKS_UPDATE)
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

    # session + artist
    expected_num_queries = 2

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

    @patch("pcapi.routes.backoffice.artists.blueprint.async_index_artist_ids")
    def test_merge_artists_success(self, mock_async_index_artist_ids, db_session, authenticated_client):
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
        mock_async_index_artist_ids.assert_called_once_with(
            [artist_to_keep.id, artist_to_delete_id], reason=IndexationReason.ARTIST_LINKS_UPDATE
        )
        assert (
            f"L'artiste {artist_to_delete.name} a été fusionné dans {artist_to_keep.name}."
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

    # session + artist
    expected_num_queries = 2

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

    @patch("pcapi.routes.backoffice.artists.blueprint.async_index_artist_ids")
    def test_split_artist_success(self, mock_async_index_artist_ids, db_session, authenticated_client):
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
            f"L'artiste a été séparé avec succès. Le nouvel artiste {new_artist_name} a été créé."
            in html_parser.extract_alerts(response.data)
        )

        new_artist = db_session.query(artist_models.Artist).filter_by(name="New Split Artist").one()
        mock_async_index_artist_ids.assert_called_once_with(
            [source_artist.id, new_artist.id], reason=IndexationReason.ARTIST_CREATION
        )
        assert product_to_move in new_artist.products


class ListArtistsTest(GetEndpointHelper):
    endpoint = "backoffice_web.artist.list_artists"
    needed_permission = perm_models.Permissions.READ_OFFERS

    # - session + user
    # - artists
    expected_num_queries = 2

    @pytest.fixture
    def artists(self, db_session):
        now = date_utils.get_naive_utc_now()
        artist1 = artist_factories.ArtistFactory(
            name="Daniel Balavoine",
            image="http://example.com/image1.jpg",
            is_blacklisted=False,
            date_created=now - datetime.timedelta(days=1),
        )
        artist_factories.ArtistAliasFactory(artist=artist1, artist_alias_name="Balavoine Daniel")
        artist_factories.ArtistAliasFactory(artist=artist1, artist_alias_name="Daniel B.")
        artist_factories.ArtistAliasFactory(artist=artist1, artist_alias_name="Balavoine D.")

        offers_factories.ProductFactory(artists=[artist1], name="Je ne suis pas un héros")

        artist2 = artist_factories.ArtistFactory(
            name="Édith Piaf", is_blacklisted=True, date_created=now - datetime.timedelta(days=10)
        )

        artist3 = artist_factories.ArtistFactory(
            name="Charles Aznavour", is_blacklisted=False, date_created=now - datetime.timedelta(days=5)
        )
        offers_factories.ProductFactory(artists=[artist3], name="La Bohème")

        db_session.flush()
        return [artist1, artist2, artist3]

    def test_list_artists_without_filter_shows_empty_table(self, authenticated_client):
        with assert_num_queries(self.expected_num_queries - 1):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        assert html_parser.count_table_rows(response.data) == 0

    def test_list_artists_by_id(self, authenticated_client, artists):
        artist_to_find = artists[0]
        query_args = {
            "search-0-search_field": "ID",
            "search-0-operator": "EQUALS",
            "search-0-string": artist_to_find.id,
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        row = rows[0]

        assert artist_to_find.id in row["ID"]
        assert row["Nom"] == "Daniel Balavoine"
        assert row["Statut"] == "Visible"
        assert row["Produits associés"] == "1"
        assert row["Alias"] == "3"

        soup = html_parser.get_soup(response.data)
        img_div = soup.find("div", style=f"background-image: url('{artist_to_find.image}')")
        assert img_div is not None

    def test_list_artists_by_name(self, authenticated_client, artists):
        artist_to_find = artists[0]
        query_args = {
            "search-0-search_field": "NAME_OR_ALIAS",
            "search-0-operator": "EQUALS",
            "search-0-string": artist_to_find.name.lower(),
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        row = rows[0]
        assert row["Nom"] == artist_to_find.name

    def test_list_artists_by_alias_name(self, authenticated_client, artists):
        query_args = {
            "search-0-search_field": "NAME_OR_ALIAS",
            "search-0-operator": "EQUALS",
            "search-0-string": "Balavoine Daniel",
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Nom"] == "Daniel Balavoine"

    @pytest.mark.parametrize(
        "is_visible, expected_names",
        [
            ("true", {"Daniel Balavoine", "Charles Aznavour"}),
            ("false", {"Édith Piaf"}),
        ],
    )
    def test_list_artists_by_visibility(self, authenticated_client, artists, is_visible, expected_names):
        query_args = {
            "search-0-search_field": "IS_VISIBLE",
            "search-0-operator": "EQUALS",
            "search-0-boolean": is_visible,
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == len(expected_names)
        found_names = {row["Nom"] for row in rows}
        assert found_names == expected_names

    def test_list_artists_by_product_name(self, authenticated_client, artists):
        query_args = {
            "search-0-search_field": "PRODUCT_NAME",
            "search-0-operator": "EQUALS",
            "search-0-string": "La Bohème",
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Nom"] == "Charles Aznavour"

    def test_list_artists_by_creation_date(self, authenticated_client, artists):
        query_args = {
            "search-0-search_field": "CREATION_DATE",
            "search-0-operator": "DATE_FROM",
            "search-0-date": (date_utils.get_naive_utc_now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
        }

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert {row["Nom"] for row in rows} == {"Daniel Balavoine", "Charles Aznavour"}

    def test_list_artists_with_multiple_filters(self, authenticated_client, artists):
        query_args = {
            "search-0-search_field": "IS_VISIBLE",
            "search-0-operator": "EQUALS",
            "search-0-boolean": "true",
            "search-1-search_field": "NAME_OR_ALIAS",
            "search-1-operator": "CONTAINS",
            "search-1-string": "Balavoine",
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["Nom"] == "Daniel Balavoine"

    def test_list_artists_without_sort_should_not_have_created_date_sort_link(self, authenticated_client, artists):
        query_args = {
            "search-0-search_field": "NAME_OR_ALIAS",
            "search-0-operator": "CONTAINS",
            "search-0-string": "Balavoine",
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        assert "sort=date_created&amp;order=desc" not in str(response.data)

    def test_list_offers_with_sort_should_have_created_date_sort_link(self, authenticated_client, artists):
        query_args = {
            "search-0-search_field": "IS_VISIBLE",
            "search-0-operator": "EQUALS",
            "search-0-boolean": "false",
            "sort": "date_created",
            "order": "asc",
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        assert "sort=date_created&amp;order=desc" in str(response.data)

    def test_list_artists_by_invalid_field_returns_400(self, authenticated_client):
        query_args = {"search-0-search_field": "WRONG_FIELD", "search-0-operator": "EQUALS"}
        with assert_num_queries(2):  # only session + rollback
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 400

        assert "Le filtre WRONG_FIELD est invalide." in html_parser.extract_alert(response.data)

    def test_list_artists_by_unsupported_operator_returns_400(self, authenticated_client):
        query_args = {
            "search-0-search_field": "NAME_OR_ALIAS",
            "search-0-operator": "GREATER_THAN",
            "search-0-string": "test",
        }
        with assert_num_queries(2):  # only session + rollback
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 400

        assert "n'est pas supporté par le filtre Nom ou alias." in html_parser.extract_alert(response.data)
