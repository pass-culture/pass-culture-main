import datetime

from flask import url_for
import pytest

from pcapi.core.categories import subcategories
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import factories as perm_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.routes.backoffice.filters import format_date

from .helpers import html_parser
from .helpers.get import GetEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


@pytest.mark.features(WIP_ENABLE_BO_OFFER_DETAILS_V2=False)
class LegacyGetOfferDetailsTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer.get_offer_details"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.READ_OFFERS

    # session + user + offer with joined data
    expected_num_queries = 3
    expected_num_queries_with_ff = 4

    def test_get_detail_offer(self, authenticated_client):
        offer = offers_factories.OfferFactory(
            description="Une offre pour tester",
            withdrawalDetails="Demander à la caisse",
            bookingContact="contact@example.com",
            bookingEmail="offre@example.com",
            ean="1234567891234",
            extraData={"author": "Author", "editeur": "Editor", "gtl_id": "08010000"},
        )
        offers_factories.OfferComplianceFactory(
            offer=offer,
            compliance_score=55,
            compliance_reasons=["stock_price", "offer_subcategory_id", "offer_description"],
        )
        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        card_text = cards_text[0]
        assert f"Offer ID : {offer.id}" in card_text
        assert "Catégorie : Films, vidéos" in card_text
        assert "Sous-catégorie : Support physique (DVD, Blu-ray...)" in card_text
        assert "Type de musique : Alternatif" in card_text
        assert "Statut : Épuisée" in card_text
        assert "État : • Validée" in card_text
        assert "Score data : 55 " in card_text
        assert "Raison de score faible : Prix Sous-catégorie Description de l'offre " in card_text
        assert "Entité juridique : Le Petit Rintintin Management" in card_text
        assert "Partenaire culturel : Le Petit Rintintin" in card_text
        assert "Utilisateur de la dernière validation" not in card_text
        assert "Date de dernière validation" not in card_text
        assert "Resynchroniser l'offre dans Algolia" in card_text
        assert "Modifier le partenaire culturel" not in card_text

        content = html_parser.content_as_text(response.data)
        assert "Auteur : Author" in content
        assert "EAN : 1234567891234" in content
        assert "Éditeur : Editor" in content
        assert "Description : Une offre pour tester " in content
        assert "Informations de retrait : Demander à la caisse " in content
        assert "Email de contact : contact@example.com " in content
        assert "Email auquel envoyer les notifications : offre@example.com " in content

        assert html_parser.count_table_rows(response.data) == 0

    def test_get_detail_offer_with_product(self, authenticated_client):
        product = offers_factories.ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id, name="good book")
        offer = offers_factories.OfferFactory(product=product)
        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

    def test_get_detail_event_offer(self, authenticated_client):
        product = offers_factories.ProductFactory(
            name="good movie",
            subcategoryId=subcategories.SEANCE_CINE.id,
            durationMinutes=133,
            description="description",
            extraData={
                "cast": [
                    "first actor",
                    "second actor",
                    "third actor",
                ],
                "type": "FEATURE_FILM",
                "visa": "123456",
                "genres": [
                    "ADVENTURE",
                    "ANIMATION",
                    "DRAMA",
                ],
                "theater": {
                    "allocine_room_id": "W1234",
                    "allocine_movie_id": 654321,
                },
                "companies": [
                    {
                        "company": {
                            "name": "Company1 Name",
                        },
                        "activity": "InternationalDistributionExports",
                    },
                    {
                        "company": {
                            "name": "Company2 Name",
                        },
                        "activity": "Distribution",
                    },
                    {
                        "company": {
                            "name": "Company3 Name",
                        },
                        "activity": "Production",
                    },
                    {
                        "company": {"name": "Company4 Name"},
                        "activity": "Production",
                    },
                    {
                        "company": {"name": "Company5 Name"},
                        "activity": "PrAgency",
                    },
                ],
                "countries": [
                    "Never Land",
                ],
                "releaseDate": "2023-04-12",
                "stageDirector": "Georges Méliès",
                "diffusionVersion": "VO",
                "performer": "John Doe",
            },
        )
        offer = offers_factories.OfferFactory(
            product=product,
            offererAddress=None,
            idAtProvider="pouet provider",
            isActive=True,
            isDuo=False,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=False,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=False,
        )

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)

        response = authenticated_client.get(url)
        assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        card_text = cards_text[0]
        assert f"Offer ID : {offer.id}" in card_text
        assert "Catégorie : Cinéma" in card_text
        assert "Sous-catégorie : Séance de cinéma " in card_text
        assert f"Produit : good movie ({product.id})" in card_text
        assert "Genres : ADVENTURE, ANIMATION, DRAMA " in card_text
        assert "Statut : Épuisée" in card_text
        assert "État : • Validée" in card_text
        assert "Entité juridique : Le Petit Rintintin Management" in card_text
        assert "Partenaire culturel : Le Petit Rintintin" in card_text
        assert "Adresse :" not in card_text  # no offererAddress
        assert "Utilisateur de la dernière validation" not in card_text
        assert "Date de dernière validation" not in card_text
        assert "Resynchroniser l'offre dans Algolia" in card_text
        assert "Modifier le partenaire culturel" not in card_text

        content = html_parser.content_as_text(response.data)
        assert "Identifiant chez le fournisseur : pouet provider" in content
        assert "Langue : VO" in content
        assert "Durée : 133 minutes" in content
        assert "Accessible aux handicaps auditifs : Oui" in content
        assert "Accessible aux handicaps mentaux : Non" in content
        assert "Accessible aux handicaps moteurs : Non renseigné" in content
        assert "Accessible aux handicaps visuels : Non" in content
        assert "Description : description" in content
        assert "Interprète : John Doe" in content

        assert html_parser.count_table_rows(response.data) == 0

    def test_get_detail_validated_offer(self, legit_user, authenticated_client):
        validation_date = datetime.datetime.utcnow()
        offer = offers_factories.OfferFactory(
            lastValidationDate=validation_date,
            validation=offers_models.OfferValidationStatus.APPROVED,
            lastValidationAuthor=legit_user,
        )

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        card_text = cards_text[0]
        assert f"Utilisateur de la dernière validation : {legit_user.full_name}" in card_text
        assert f"Date de dernière validation : {format_date(validation_date, '%d/%m/%Y à %Hh%M')}" in card_text

    def test_get_detail_offer_without_show_subtype(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory(
            withdrawalDetails="Demander à la caisse",
            extraData={"showType": 1510},
        )

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

    def test_get_detail_offer_display_modify_offer_button(self, client):
        offer = offers_factories.OfferFactory()
        manage_offers = perm_models.Permission.query.filter_by(name=perm_models.Permissions.MANAGE_OFFERS.name).one()
        read_offers = perm_models.Permission.query.filter_by(name=perm_models.Permissions.READ_OFFERS.name).one()
        role = perm_factories.RoleFactory(permissions=[read_offers, manage_offers])
        user = users_factories.UserFactory()
        user.backoffice_profile = perm_models.BackOfficeUserProfile(user=user, roles=[role])

        authenticated_client = client.with_bo_session_auth(user)
        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        card_text = cards_text[0]

        assert "Modifier l'offre" in card_text
        assert "Valider l'offre" not in card_text
        assert "Rejeter l'offre" not in card_text

    def test_get_detail_offer_display_validation_buttons_fraud(self, client):
        offer = offers_factories.OfferFactory()
        pro_fraud_actions = perm_models.Permission.query.filter_by(
            name=perm_models.Permissions.PRO_FRAUD_ACTIONS.name
        ).one()
        read_offers = perm_models.Permission.query.filter_by(name=perm_models.Permissions.READ_OFFERS.name).one()
        role = perm_factories.RoleFactory(permissions=[read_offers, pro_fraud_actions])
        user = users_factories.UserFactory()
        user.backoffice_profile = perm_models.BackOfficeUserProfile(user=user, roles=[role])

        authenticated_client = client.with_bo_session_auth(user)
        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        card_text = cards_text[0]

        assert "Modifier l'offre" not in card_text
        assert "Valider l'offre" in card_text
        assert "Rejeter l'offre" in card_text

    def test_get_detail_rejected_offer(self, legit_user, authenticated_client):
        validation_date = datetime.datetime.utcnow()
        offer = offers_factories.OfferFactory(
            lastValidationDate=validation_date,
            validation=offers_models.OfferValidationStatus.REJECTED,
            lastValidationAuthor=legit_user,
        )

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        card_text = cards_text[0]
        assert f"Utilisateur de la dernière validation : {legit_user.full_name}" in card_text
        assert f"Date de dernière validation : {format_date(validation_date, '%d/%m/%Y à %Hh%M')}" in card_text

    def test_get_offer_details_with_one_expired_stock(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)

        expired_stock = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(hours=1), price=6.66
        )

        query_count = self.expected_num_queries_with_ff
        query_count += 1  # _get_editable_stock
        query_count += 1  # check_can_move_event_offer

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(query_count):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        stocks_rows = html_parser.extract_table_rows(response.data)
        assert len(stocks_rows) == 1
        assert stocks_rows[0]["Stock ID"] == str(expired_stock.id)
        assert stocks_rows[0]["Stock réservé"] == "0"
        assert stocks_rows[0]["Stock restant"] == "0"
        assert stocks_rows[0]["Prix"] == "6,66 €"
        assert stocks_rows[0]["Date / Heure"] == format_date(expired_stock.beginningDatetime, "%d/%m/%Y à %Hh%M")

    def test_get_offer_details_with_two_expired_stocks(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)

        expired_stock_1 = offers_factories.EventStockFactory(
            offer=offer,
            quantity=100,
            dnBookedQuantity=70,
            beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(hours=2),
        )
        expired_stock_2 = offers_factories.EventStockFactory(
            offer=offer,
            quantity=None,
            dnBookedQuantity=25,
            beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(hours=1),
        )

        query_count = self.expected_num_queries_with_ff
        query_count += 1  # _get_editable_stock
        query_count += 1  # check_can_move_event_offer

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(query_count):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        stocks_rows = html_parser.extract_table_rows(response.data)
        assert len(stocks_rows) == 2
        assert stocks_rows[1]["Stock ID"] == str(expired_stock_1.id)
        assert stocks_rows[1]["Stock réservé"] == "70"
        assert stocks_rows[1]["Stock restant"] == "0"
        assert stocks_rows[1]["Prix"] == "10,10 €"
        assert stocks_rows[1]["Date / Heure"] == format_date(expired_stock_1.beginningDatetime, "%d/%m/%Y à %Hh%M")

        assert stocks_rows[0]["Stock ID"] == str(expired_stock_2.id)
        assert stocks_rows[0]["Stock réservé"] == "25"
        assert stocks_rows[0]["Stock restant"] == "0"
        assert stocks_rows[0]["Prix"] == "10,10 €"
        assert stocks_rows[0]["Date / Heure"] == format_date(expired_stock_2.beginningDatetime, "%d/%m/%Y à %Hh%M")

    @pytest.mark.parametrize(
        "quantity,booked_quantity,expected_remaining,venue_factory,expected_price",
        [
            (1000, 0, "1000", offerers_factories.VenueFactory, "10,10 €"),
            (1000, 50, "950", offerers_factories.VenueFactory, "10,10 €"),
            (1000, 1000, "0", offerers_factories.VenueFactory, "10,10 €"),
            (None, 0, "Illimité", offerers_factories.VenueFactory, "10,10 €"),
            (None, 50, "Illimité", offerers_factories.CaledonianVenueFactory, "10,10 € (1205 CFP)"),
        ],
    )
    def test_get_offer_details_with_one_bookable_stock(
        self,
        legit_user,
        authenticated_client,
        quantity,
        booked_quantity,
        expected_remaining,
        venue_factory,
        expected_price,
    ):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id, venue=venue_factory())
        stock = offers_factories.EventStockFactory(offer=offer, quantity=quantity, dnBookedQuantity=booked_quantity)

        query_count = self.expected_num_queries_with_ff
        query_count += 1  # _get_editable_stock
        query_count += 3  # check_can_move_event_offer

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(query_count):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        stocks_rows = html_parser.extract_table_rows(response.data)
        assert len(stocks_rows) == 1
        assert stocks_rows[0]["Stock ID"] == str(stock.id)
        assert stocks_rows[0]["Stock réservé"] == str(booked_quantity)
        assert stocks_rows[0]["Stock restant"] == expected_remaining
        assert stocks_rows[0]["Prix"] == expected_price
        assert stocks_rows[0]["Date / Heure"] == format_date(stock.beginningDatetime, "%d/%m/%Y à %Hh%M")

    def test_get_offer_details_with_soft_deleted_stock(self, authenticated_client):
        stock = offers_factories.EventStockFactory(quantity=0, dnBookedQuantity=0, isSoftDeleted=True)

        query_count = self.expected_num_queries_with_ff
        query_count += 1  # _get_editable_stock
        query_count += 3  # check_can_move_event_offer

        url = url_for(self.endpoint, offer_id=stock.offer.id)
        with assert_num_queries(query_count):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        stocks_rows = html_parser.extract_table_rows(response.data, parent_class="stock-tab-pane")
        assert len(stocks_rows) == 1
        assert stocks_rows[0]["Stock ID"] == str(stock.id)
        assert stocks_rows[0]["Stock réservé"] == "0"
        assert stocks_rows[0]["Stock restant"] == "supprimé"
        assert stocks_rows[0]["Prix"] == "10,10 €"
        assert stocks_rows[0]["Date / Heure"] == format_date(stock.beginningDatetime, "%d/%m/%Y à %Hh%M")

    @pytest.mark.parametrize(
        "venue_factory,expected_price_1,expected_price_2,expected_price_3,expected_price_4",
        [
            (offerers_factories.VenueFactory, "0,00 €", "13,00 €", "42,00 €", "66,60 €"),
            (
                offerers_factories.CaledonianVenueFactory,
                "0,00 € (0 CFP)",
                "13,00 € (1551 CFP)",
                "42,00 € (5012 CFP)",
                "66,60 € (7947 CFP)",
            ),
        ],
    )
    def test_get_offer_details_with_price_categories(
        self,
        authenticated_client,
        venue_factory,
        expected_price_1,
        expected_price_2,
        expected_price_3,
        expected_price_4,
    ):
        venue = venue_factory()
        offer = offers_factories.EventOfferFactory(venue=venue)
        price_gold = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel__label="OR", price=66.6, priceCategoryLabel__venue=venue
        )
        price_silver = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel__label="ARGENT", price=42, priceCategoryLabel__venue=venue
        )
        price_bronze = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel__label="BRONZE", price=13, priceCategoryLabel__venue=venue
        )
        price_free = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel__label="GRATUIT", price=0, priceCategoryLabel__venue=venue
        )

        offers_factories.EventStockFactory(offer=offer, priceCategory=price_gold)
        offers_factories.EventStockFactory(offer=offer, priceCategory=price_silver)
        offers_factories.EventStockFactory(offer=offer, priceCategory=price_bronze)
        offers_factories.EventStockFactory(offer=offer, priceCategory=price_free)

        query_count = self.expected_num_queries_with_ff
        query_count += 1  # _get_editable_stock
        query_count += 3  # check_can_move_event_offer

        url = url_for(self.endpoint, offer_id=offer.id)
        with assert_num_queries(query_count):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        stocks_rows = html_parser.extract_table_rows(response.data, parent_class="stock-tab-pane")
        assert len(stocks_rows) == 4
        assert stocks_rows[0]["Tarif"] == "GRATUIT"
        assert stocks_rows[0]["Prix"] == expected_price_1
        assert stocks_rows[1]["Tarif"] == "BRONZE"
        assert stocks_rows[1]["Prix"] == expected_price_2
        assert stocks_rows[2]["Tarif"] == "ARGENT"
        assert stocks_rows[2]["Prix"] == expected_price_3
        assert stocks_rows[3]["Tarif"] == "OR"
        assert stocks_rows[3]["Prix"] == expected_price_4

    def test_get_offer_details_stocks_sorted_by_event_date_desc(self, authenticated_client):
        now = datetime.datetime.utcnow()
        offer = offers_factories.EventOfferFactory()
        stock1 = offers_factories.EventStockFactory(offer=offer, beginningDatetime=now + datetime.timedelta(days=5))
        stock2 = offers_factories.EventStockFactory(offer=offer, beginningDatetime=now + datetime.timedelta(days=9))
        stock3 = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=now + datetime.timedelta(days=7), isSoftDeleted=True
        )

        query_count = self.expected_num_queries_with_ff
        query_count += 1  # _get_editable_stock
        query_count += 3  # check_can_move_event_offer

        url = url_for(self.endpoint, offer_id=offer.id)
        with assert_num_queries(query_count):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        stocks_rows = html_parser.extract_table_rows(response.data, parent_class="stock-tab-pane")
        assert [row["Stock ID"] for row in stocks_rows] == [str(stock2.id), str(stock3.id), str(stock1.id)]

    def test_get_event_offer(self, legit_user, authenticated_client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.VenueFactory.create_batch(2, managingOfferer=venue.managingOfferer, pricing_point=venue)
        offer = offers_factories.EventOfferFactory(venue=venue)

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        # Additional queries to check if "Modifier le partenaire culturel" should be displayed or not":
        # - _get_editable_stock
        # - count stocks with beginningDatetime in the past
        # - count reimbursed bookings
        # - fetch destination venue candidates
        with assert_num_queries(self.expected_num_queries_with_ff + 4):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        cards_text = html_parser.extract_cards_text(response.data)
        assert len(cards_text) == 1
        assert "Modifier le partenaire culturel" in cards_text[0]

    def test_get_offer_details(self, authenticated_client):
        address = geography_factories.AddressFactory(
            street="1v Place Jacques Rueff",
            postalCode="75007",
            city="Paris",
            latitude=48.85605,
            longitude=2.298,
            inseeCode="75107",
            banId="75107_4803_00001_v",
        )
        offerer_adress = offerers_factories.OffererAddressFactory(label="Champ de Mars", address=address)
        offer = offers_factories.OfferFactory(
            offererAddressId=offerer_adress.id, venue__managingOfferer=offerer_adress.offerer
        )

        url = url_for(self.endpoint, offer_id=offer.id)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        text = html_parser.extract_cards_text(response.data)[0]
        assert "Localisation : Champ de Mars 1v Place Jacques Rueff 75007 Paris 48.85605, 2.29800" in text

    def test_get_offer_details_with_offerer_confidence_rule(self, authenticated_client):
        rule = offerers_factories.ManualReviewOffererConfidenceRuleFactory(offerer__name="Offerer")
        offer = offers_factories.OfferFactory(venue__managingOfferer=rule.offerer)

        url = url_for(self.endpoint, offer_id=offer.id)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        text = html_parser.extract_cards_text(response.data)[0]
        assert "Entité juridique : Offerer Revue manuelle" in text

    def test_get_offer_details_with_venue_confidence_rule(self, authenticated_client):
        rule = offerers_factories.ManualReviewVenueConfidenceRuleFactory(venue__name="Venue")
        offer = offers_factories.OfferFactory(venue=rule.venue)

        url = url_for(self.endpoint, offer_id=offer.id)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        text = html_parser.extract_cards_text(response.data)[0]
        assert "Partenaire culturel : Venue Revue manuelle" in text

    def test_collective_offer_with_top_acteur_offerer(self, authenticated_client):
        offer = offers_factories.OfferFactory(
            venue__managingOfferer__name="Offerer",
            venue__managingOfferer__tags=[offerers_factories.OffererTagFactory(name="top-acteur", label="Top Acteur")],
        )

        url = url_for(self.endpoint, offer_id=offer.id)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        text = html_parser.extract_cards_text(response.data)[0]
        assert "Entité juridique : Offerer Top Acteur" in text


@pytest.mark.features(WIP_ENABLE_BO_OFFER_DETAILS_V2=True)
class GetOfferDetailsTest(GetEndpointHelper):
    endpoint = "backoffice_web.offer.get_offer_details"
    endpoint_kwargs = {"offer_id": 1}
    needed_permission = perm_models.Permissions.READ_OFFERS

    # session + user + offer with joined data
    expected_num_queries = 3
    expected_num_queries_with_ff = 4

    def test_get_detail_offer(self, authenticated_client):
        offer = offers_factories.OfferFactory(
            description="Une offre pour tester",
            withdrawalDetails="Demander à la caisse",
            bookingContact="contact@example.com",
            bookingEmail="offre@example.com",
            ean="1234567891234",
            extraData={"author": "Author", "editeur": "Editor", "gtl_id": "08010000"},
        )
        offers_factories.OfferComplianceFactory(
            offer=offer,
            compliance_score=55,
            compliance_reasons=["stock_price", "offer_subcategory_id", "offer_description"],
        )
        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        descriptions = html_parser.extract_descriptions(response.data)
        assert str(offer.id) == descriptions["Offer ID"]
        assert descriptions["Catégorie"] == "Films, vidéos"
        assert descriptions["Sous-catégorie"] == "Support physique (DVD, Blu-ray...)"
        assert descriptions["Type de musique"] == "Alternatif"
        assert descriptions["Statut"] == "Épuisée"
        assert descriptions["Score data"] == "55"
        assert descriptions["Raison de score faible"] == "Prix Sous-catégorie Description de l'offre"
        assert descriptions["Entité juridique"].startswith("Le Petit Rintintin Management")
        assert descriptions["Partenaire culturel"].startswith("Le Petit Rintintin")
        assert "Utilisateur de la dernière validation" not in descriptions
        assert "Date de dernière validation" not in descriptions
        assert descriptions["Auteur"] == "Author"
        assert descriptions["EAN"] == "1234567891234"
        assert descriptions["Éditeur"] == "Editor"
        assert descriptions["Description"] == "Une offre pour tester"
        assert descriptions["Informations de retrait"] == "Demander à la caisse"
        assert descriptions["Email de contact"] == "contact@example.com"
        assert descriptions["Email auquel envoyer les notifications"] == "offre@example.com"

        buttons = html_parser.extract(response.data, "button")
        assert "Resync. Algolia" in buttons

        badges = html_parser.extract_badges(response.data)
        assert "• Validée" in badges

        assert html_parser.count_table_rows(response.data) == 0

    def test_get_detail_offer_with_product(self, authenticated_client):
        product = offers_factories.ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id, name="good book")
        offer = offers_factories.OfferFactory(product=product)
        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

    def test_get_detail_event_offer(self, authenticated_client):
        product = offers_factories.ProductFactory(
            name="good movie",
            subcategoryId=subcategories.SEANCE_CINE.id,
            durationMinutes=133,
            description="description",
            extraData={
                "cast": [
                    "first actor",
                    "second actor",
                    "third actor",
                ],
                "type": "FEATURE_FILM",
                "visa": "123456",
                "genres": [
                    "ADVENTURE",
                    "ANIMATION",
                    "DRAMA",
                ],
                "theater": {
                    "allocine_room_id": "W1234",
                    "allocine_movie_id": 654321,
                },
                "companies": [
                    {
                        "company": {
                            "name": "Company1 Name",
                        },
                        "activity": "InternationalDistributionExports",
                    },
                    {
                        "company": {
                            "name": "Company2 Name",
                        },
                        "activity": "Distribution",
                    },
                    {
                        "company": {
                            "name": "Company3 Name",
                        },
                        "activity": "Production",
                    },
                    {
                        "company": {"name": "Company4 Name"},
                        "activity": "Production",
                    },
                    {
                        "company": {"name": "Company5 Name"},
                        "activity": "PrAgency",
                    },
                ],
                "countries": [
                    "Never Land",
                ],
                "releaseDate": "2023-04-12",
                "stageDirector": "Georges Méliès",
                "diffusionVersion": "VO",
                "performer": "John Doe",
            },
        )
        offer = offers_factories.OfferFactory(
            product=product,
            offererAddress=None,
            idAtProvider="pouet provider",
            isActive=True,
            isDuo=False,
            audioDisabilityCompliant=True,
            mentalDisabilityCompliant=False,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=False,
        )

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)

        response = authenticated_client.get(url)
        assert response.status_code == 200

        descriptions = html_parser.extract_descriptions(response.data)
        assert descriptions["Offer ID"] == str(offer.id)
        assert descriptions["Catégorie"] == "Cinéma"
        assert descriptions["Sous-catégorie"] == "Séance de cinéma"
        assert descriptions["Produit"] == f"good movie ({product.id})"
        assert descriptions["Genres"] == "ADVENTURE, ANIMATION, DRAMA"
        assert descriptions["Statut"] == "Épuisée"
        assert descriptions["Entité juridique"].startswith("Le Petit Rintintin Management")
        assert descriptions["Partenaire culturel"].startswith("Le Petit Rintintin")
        assert "Adresse" not in descriptions
        assert "Utilisateur de la dernière validation" not in descriptions
        assert "Date de la dernière validation" not in descriptions

        assert descriptions["Identifiant chez le fournisseur"] == "pouet provider"
        assert descriptions["Langue"] == "VO"
        assert descriptions["Durée"] == "133 minutes"
        assert descriptions["Description"] == "description"
        assert descriptions["Interprète"] == "John Doe"

        accessibility_badges = html_parser.extract_accessibility_badges(response.data)
        assert accessibility_badges["Handicap auditif"] is True
        assert accessibility_badges["Handicap mental"] is False
        assert accessibility_badges["Handicap moteur"] is False
        assert accessibility_badges["Handicap visuel"] is False

        badges = html_parser.extract_badges(response.data)
        assert "• Validée" in badges

        buttons = html_parser.extract(response.data, "button")
        assert "Resync. Algolia" in buttons
        assert "Modifier le partenaire culturel" not in buttons

        assert html_parser.count_table_rows(response.data) == 0

    def test_get_detail_validated_offer(self, legit_user, authenticated_client):
        validation_date = datetime.datetime.utcnow()
        offer = offers_factories.OfferFactory(
            lastValidationDate=validation_date,
            validation=offers_models.OfferValidationStatus.APPROVED,
            lastValidationAuthor=legit_user,
        )

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        descriptions = html_parser.extract_descriptions(response.data)
        assert descriptions["Utilisateur de la dernière validation"] == legit_user.full_name
        assert descriptions["Date de la dernière validation"] == format_date(validation_date, "%d/%m/%Y à %Hh%M")

    def test_get_detail_offer_without_show_subtype(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory(
            withdrawalDetails="Demander à la caisse",
            extraData={"showType": 1510},
        )

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

    def test_get_detail_offer_display_modify_offer_button(self, client):
        offer = offers_factories.OfferFactory()
        manage_offers = perm_models.Permission.query.filter_by(name=perm_models.Permissions.MANAGE_OFFERS.name).one()
        read_offers = perm_models.Permission.query.filter_by(name=perm_models.Permissions.READ_OFFERS.name).one()
        role = perm_factories.RoleFactory(permissions=[read_offers, manage_offers])
        user = users_factories.UserFactory()
        user.backoffice_profile = perm_models.BackOfficeUserProfile(user=user, roles=[role])

        authenticated_client = client.with_bo_session_auth(user)
        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        buttons = html_parser.extract(response.data, "button")
        assert "Taguer/Pondérer" in buttons
        assert "Valider l'offre" not in buttons
        assert "Rejeter l'offre" not in buttons

    def test_get_detail_offer_display_validation_buttons_fraud(self, client):
        offer = offers_factories.OfferFactory()
        pro_fraud_actions = perm_models.Permission.query.filter_by(
            name=perm_models.Permissions.PRO_FRAUD_ACTIONS.name
        ).one()
        read_offers = perm_models.Permission.query.filter_by(name=perm_models.Permissions.READ_OFFERS.name).one()
        role = perm_factories.RoleFactory(permissions=[read_offers, pro_fraud_actions])
        user = users_factories.UserFactory()
        user.backoffice_profile = perm_models.BackOfficeUserProfile(user=user, roles=[role])

        authenticated_client = client.with_bo_session_auth(user)
        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        buttons = html_parser.extract(response.data, "button")
        assert "Taguer/Pondérer" not in buttons
        assert "Valider" in buttons
        assert "Rejeter" in buttons

    def test_get_detail_rejected_offer(self, legit_user, authenticated_client):
        validation_date = datetime.datetime.utcnow()
        offer = offers_factories.OfferFactory(
            lastValidationDate=validation_date,
            validation=offers_models.OfferValidationStatus.REJECTED,
            lastValidationAuthor=legit_user,
        )

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        descriptions = html_parser.extract_descriptions(response.data)
        assert descriptions["Utilisateur de la dernière validation"] == legit_user.full_name
        assert descriptions["Date de la dernière validation"] == format_date(validation_date, "%d/%m/%Y à %Hh%M")

    def test_get_offer_details_with_one_expired_stock(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)

        expired_stock = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(hours=1), price=6.66
        )

        query_count = self.expected_num_queries_with_ff
        query_count += 1  # _get_editable_stock
        query_count += 1  # check_can_move_event_offer

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(query_count):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        stocks_rows = html_parser.extract_table_rows(response.data)
        assert len(stocks_rows) == 1
        assert stocks_rows[0]["ID"] == str(expired_stock.id)
        assert stocks_rows[0]["Stock réservé"] == "0"
        assert stocks_rows[0]["Stock restant"] == "0"
        assert stocks_rows[0]["Prix"] == "6,66 €"
        assert stocks_rows[0]["Date / Heure"] == format_date(expired_stock.beginningDatetime, "%d/%m/%Y à %Hh%M")

    def test_get_offer_details_with_two_expired_stocks(self, legit_user, authenticated_client):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)

        expired_stock_1 = offers_factories.EventStockFactory(
            offer=offer,
            quantity=100,
            dnBookedQuantity=70,
            beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(hours=2),
        )
        expired_stock_2 = offers_factories.EventStockFactory(
            offer=offer,
            quantity=None,
            dnBookedQuantity=25,
            beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(hours=1),
        )

        query_count = self.expected_num_queries_with_ff
        query_count += 1  # _get_editable_stock
        query_count += 1  # check_can_move_event_offer

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(query_count):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        stocks_rows = html_parser.extract_table_rows(response.data)
        assert len(stocks_rows) == 2
        assert stocks_rows[1]["ID"] == str(expired_stock_1.id)
        assert stocks_rows[1]["Stock réservé"] == "70"
        assert stocks_rows[1]["Stock restant"] == "0"
        assert stocks_rows[1]["Prix"] == "10,10 €"
        assert stocks_rows[1]["Date / Heure"] == format_date(expired_stock_1.beginningDatetime, "%d/%m/%Y à %Hh%M")

        assert stocks_rows[0]["ID"] == str(expired_stock_2.id)
        assert stocks_rows[0]["Stock réservé"] == "25"
        assert stocks_rows[0]["Stock restant"] == "0"
        assert stocks_rows[0]["Prix"] == "10,10 €"
        assert stocks_rows[0]["Date / Heure"] == format_date(expired_stock_2.beginningDatetime, "%d/%m/%Y à %Hh%M")

    @pytest.mark.parametrize(
        "quantity,booked_quantity,expected_remaining,venue_factory,expected_price",
        [
            (1000, 0, "1000", offerers_factories.VenueFactory, "10,10 €"),
            (1000, 50, "950", offerers_factories.VenueFactory, "10,10 €"),
            (1000, 1000, "0", offerers_factories.VenueFactory, "10,10 €"),
            (None, 0, "Illimité", offerers_factories.VenueFactory, "10,10 €"),
            (None, 50, "Illimité", offerers_factories.CaledonianVenueFactory, "10,10 € (1205 CFP)"),
        ],
    )
    def test_get_offer_details_with_one_bookable_stock(
        self,
        legit_user,
        authenticated_client,
        quantity,
        booked_quantity,
        expected_remaining,
        venue_factory,
        expected_price,
    ):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id, venue=venue_factory())
        stock = offers_factories.EventStockFactory(offer=offer, quantity=quantity, dnBookedQuantity=booked_quantity)

        query_count = self.expected_num_queries_with_ff
        query_count += 1  # _get_editable_stock
        query_count += 3  # check_can_move_event_offer

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        with assert_num_queries(query_count):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        stocks_rows = html_parser.extract_table_rows(response.data)
        assert len(stocks_rows) == 1
        assert stocks_rows[0]["ID"] == str(stock.id)
        assert stocks_rows[0]["Stock réservé"] == str(booked_quantity)
        assert stocks_rows[0]["Stock restant"] == expected_remaining
        assert stocks_rows[0]["Prix"] == expected_price
        assert stocks_rows[0]["Date / Heure"] == format_date(stock.beginningDatetime, "%d/%m/%Y à %Hh%M")

    def test_get_offer_details_with_soft_deleted_stock(self, authenticated_client):
        stock = offers_factories.EventStockFactory(quantity=0, dnBookedQuantity=0, isSoftDeleted=True)

        query_count = self.expected_num_queries_with_ff
        query_count += 1  # _get_editable_stock
        query_count += 3  # check_can_move_event_offer

        url = url_for(self.endpoint, offer_id=stock.offer.id)
        with assert_num_queries(query_count):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        stocks_rows = html_parser.extract_table_rows(response.data)
        assert len(stocks_rows) == 1
        assert stocks_rows[0]["ID"] == str(stock.id)
        assert stocks_rows[0]["Stock réservé"] == "0"
        assert stocks_rows[0]["Stock restant"] == "supprimé"
        assert stocks_rows[0]["Prix"] == "10,10 €"
        assert stocks_rows[0]["Date / Heure"] == format_date(stock.beginningDatetime, "%d/%m/%Y à %Hh%M")

    @pytest.mark.parametrize(
        "venue_factory,expected_price_1,expected_price_2,expected_price_3,expected_price_4",
        [
            (offerers_factories.VenueFactory, "0,00 €", "13,00 €", "42,00 €", "66,60 €"),
            (
                offerers_factories.CaledonianVenueFactory,
                "0,00 € (0 CFP)",
                "13,00 € (1551 CFP)",
                "42,00 € (5012 CFP)",
                "66,60 € (7947 CFP)",
            ),
        ],
    )
    def test_get_offer_details_with_price_categories(
        self,
        authenticated_client,
        venue_factory,
        expected_price_1,
        expected_price_2,
        expected_price_3,
        expected_price_4,
    ):
        venue = venue_factory()
        offer = offers_factories.EventOfferFactory(venue=venue)
        price_gold = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel__label="OR", price=66.6, priceCategoryLabel__venue=venue
        )
        price_silver = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel__label="ARGENT", price=42, priceCategoryLabel__venue=venue
        )
        price_bronze = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel__label="BRONZE", price=13, priceCategoryLabel__venue=venue
        )
        price_free = offers_factories.PriceCategoryFactory(
            offer=offer, priceCategoryLabel__label="GRATUIT", price=0, priceCategoryLabel__venue=venue
        )

        offers_factories.EventStockFactory(offer=offer, priceCategory=price_gold)
        offers_factories.EventStockFactory(offer=offer, priceCategory=price_silver)
        offers_factories.EventStockFactory(offer=offer, priceCategory=price_bronze)
        offers_factories.EventStockFactory(offer=offer, priceCategory=price_free)

        query_count = self.expected_num_queries_with_ff
        query_count += 1  # _get_editable_stock
        query_count += 3  # check_can_move_event_offer

        url = url_for(self.endpoint, offer_id=offer.id)
        with assert_num_queries(query_count):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        stocks_rows = html_parser.extract_table_rows(response.data)
        assert len(stocks_rows) == 4
        assert stocks_rows[0]["Tarif"] == "GRATUIT"
        assert stocks_rows[0]["Prix"] == expected_price_1
        assert stocks_rows[1]["Tarif"] == "BRONZE"
        assert stocks_rows[1]["Prix"] == expected_price_2
        assert stocks_rows[2]["Tarif"] == "ARGENT"
        assert stocks_rows[2]["Prix"] == expected_price_3
        assert stocks_rows[3]["Tarif"] == "OR"
        assert stocks_rows[3]["Prix"] == expected_price_4

    def test_get_offer_details_stocks_sorted_by_event_date_desc(self, authenticated_client):
        now = datetime.datetime.utcnow()
        offer = offers_factories.EventOfferFactory()
        stock1 = offers_factories.EventStockFactory(offer=offer, beginningDatetime=now + datetime.timedelta(days=5))
        stock2 = offers_factories.EventStockFactory(offer=offer, beginningDatetime=now + datetime.timedelta(days=9))
        stock3 = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=now + datetime.timedelta(days=7), isSoftDeleted=True
        )

        query_count = self.expected_num_queries_with_ff
        query_count += 1  # _get_editable_stock
        query_count += 3  # check_can_move_event_offer

        url = url_for(self.endpoint, offer_id=offer.id)
        with assert_num_queries(query_count):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        stocks_rows = html_parser.extract_table_rows(response.data)
        assert [row["ID"] for row in stocks_rows] == [str(stock2.id), str(stock3.id), str(stock1.id)]

    def test_get_event_offer(self, legit_user, authenticated_client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.VenueFactory.create_batch(2, managingOfferer=venue.managingOfferer, pricing_point=venue)
        offer = offers_factories.EventOfferFactory(venue=venue)

        url = url_for(self.endpoint, offer_id=offer.id, _external=True)
        # Additional queries to check if "Modifier le partenaire culturel" should be displayed or not":
        # - _get_editable_stock
        # - count stocks with beginningDatetime in the past
        # - count reimbursed bookings
        # - fetch destination venue candidates
        with assert_num_queries(self.expected_num_queries_with_ff + 4):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        buttons = html_parser.extract(response.data, "button")
        assert "Modifier le partenaire culturel" in buttons

    def test_get_offer_details(self, authenticated_client):
        address = geography_factories.AddressFactory(
            street="1v Place Jacques Rueff",
            postalCode="75007",
            city="Paris",
            latitude=48.85605,
            longitude=2.298,
            inseeCode="75107",
            banId="75107_4803_00001_v",
        )
        offerer_adress = offerers_factories.OffererAddressFactory(label="Champ de Mars", address=address)
        offer = offers_factories.OfferFactory(
            offererAddressId=offerer_adress.id, venue__managingOfferer=offerer_adress.offerer
        )

        url = url_for(self.endpoint, offer_id=offer.id)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        descriptions = html_parser.extract_descriptions(response.data)
        assert descriptions["Localisation"] == "Champ de Mars 1v Place Jacques Rueff 75007 Paris 48.85605, 2.29800"

    def test_get_offer_details_with_offerer_confidence_rule(self, authenticated_client):
        rule = offerers_factories.ManualReviewOffererConfidenceRuleFactory(offerer__name="Offerer")
        offer = offers_factories.OfferFactory(venue__managingOfferer=rule.offerer)

        url = url_for(self.endpoint, offer_id=offer.id)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        descriptions = html_parser.extract_descriptions(response.data)
        assert descriptions["Entité juridique"] == "Offerer Revue manuelle"

    def test_get_offer_details_with_venue_confidence_rule(self, authenticated_client):
        rule = offerers_factories.ManualReviewVenueConfidenceRuleFactory(venue__name="Venue")
        offer = offers_factories.OfferFactory(venue=rule.venue)

        url = url_for(self.endpoint, offer_id=offer.id)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        descriptions = html_parser.extract_descriptions(response.data)
        assert descriptions["Partenaire culturel"] == "Venue Revue manuelle"

    def test_collective_offer_with_top_acteur_offerer(self, authenticated_client):
        offer = offers_factories.OfferFactory(
            venue__managingOfferer__name="Offerer",
            venue__managingOfferer__tags=[offerers_factories.OffererTagFactory(name="top-acteur", label="Top Acteur")],
        )

        url = url_for(self.endpoint, offer_id=offer.id)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        descriptions = html_parser.extract_descriptions(response.data)
        assert descriptions["Entité juridique"] == "Offerer Top Acteur"
