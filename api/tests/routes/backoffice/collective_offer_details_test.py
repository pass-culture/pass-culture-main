import datetime

from flask import url_for
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import conf as finance_conf
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.routes.backoffice.filters import format_date

from .helpers import button as button_helpers
from .helpers import html_parser
from .helpers.get import GetEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


#######################################################################
# Legacy tests with WIP_ENABLE_BO_COLLECTIVE_OFFER_DETAILS_V2 = False #
#######################################################################


@pytest.mark.features(WIP_ENABLE_BO_COLLECTIVE_OFFER_DETAILS_V2=False)
class LegacyRejectCollectiveOfferFromDetailsButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
    button_label = "Rejeter l'offre"
    endpoint = "backoffice_web.collective_offer.get_collective_offer_details"

    @property
    def path(self):
        stock = educational_factories.CollectiveStockFactory()
        return url_for(self.endpoint, collective_offer_id=stock.collectiveOffer.id)


@pytest.mark.features(WIP_ENABLE_BO_COLLECTIVE_OFFER_DETAILS_V2=False)
class LegacyValidateCollectiveOfferFromDetailsButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
    button_label = "Valider l'offre"
    endpoint = "backoffice_web.collective_offer.get_collective_offer_details"

    @property
    def path(self):
        stock = educational_factories.CollectiveStockFactory()
        return url_for(self.endpoint, collective_offer_id=stock.collectiveOffer.id)


@pytest.mark.features(WIP_ENABLE_BO_COLLECTIVE_OFFER_DETAILS_V2=False)
class LegacyGetCollectiveOfferDetailTest(GetEndpointHelper):
    endpoint = "backoffice_web.collective_offer.get_collective_offer_details"
    endpoint_kwargs = {"collective_offer_id": 1}
    needed_permission = perm_models.Permissions.READ_OFFERS
    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch CollectiveOffer
    # - _is_collective_offer_price_editable
    expected_num_queries = 4
    expected_num_queries_with_ff = expected_num_queries + 1  # FF MOVE_OFFER_TEST

    def test_nominal(self, legit_user, authenticated_client):
        start_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        end_date = start_date + datetime.timedelta(days=28)
        collective_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__startDatetime=start_date,
            collectiveStock__endDatetime=end_date,
            collectiveStock__collectiveOffer__teacher=educational_factories.EducationalRedactorFactory(
                firstName="Pacôme", lastName="De Champignac"
            ),
            collectiveStock__collectiveOffer__institution=educational_factories.EducationalInstitutionFactory(
                name="Ecole de Marcinelle"
            ),
            collectiveStock__collectiveOffer__template=educational_factories.CollectiveOfferTemplateFactory(
                name="offre Vito Cortizone pour lieu que l'on ne peut refuser"
            ),
        )
        url = url_for(self.endpoint, collective_offer_id=collective_booking.collectiveStock.collectiveOffer.id)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content_as_text = html_parser.content_as_text(response.data)
        assert "Ajuster le prix de l'offre" in content_as_text
        assert (
            f"Date de l'évènement : {start_date.strftime('%d/%m/%Y')} → {end_date.strftime('%d/%m/%Y')}"
            in content_as_text
        )
        assert "Statut : Expirée" in content_as_text
        assert "Statut PC Pro : Réservée" in content_as_text
        assert "État : • Validée" in content_as_text
        assert "Utilisateur de la dernière validation" not in content_as_text
        assert "Date de dernière validation de l’offre" not in content_as_text
        assert "Enseignant : Pacôme De Champignac" in content_as_text
        assert "Établissement : Ecole de Marcinelle" in content_as_text
        assert "Offre vitrine liée : offre Vito Cortizone pour lieu que l'on ne peut refuser" in content_as_text

    def test_processed_pricing(self, legit_user, authenticated_client):
        pricing = finance_factories.CollectivePricingFactory(
            status=finance_models.PricingStatus.PROCESSED,
            collectiveBooking__collectiveStock__startDatetime=datetime.datetime(1970, 1, 1),
        )
        url = url_for(self.endpoint, collective_offer_id=pricing.collectiveBooking.collectiveStock.collectiveOffer.id)

        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert "Ajuster le prix de l'offre" not in response.data.decode()

    def test_invoiced_pricing(self, legit_user, authenticated_client):
        pricing = finance_factories.CollectivePricingFactory(
            status=finance_models.PricingStatus.INVOICED,
            collectiveBooking__collectiveStock__startDatetime=datetime.datetime(1970, 1, 1),
        )
        url = url_for(self.endpoint, collective_offer_id=pricing.collectiveBooking.collectiveStock.collectiveOffer.id)

        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        assert "Ajuster le prix de l'offre" not in response.data.decode()

    def test_cashflow_pending(self, legit_user, authenticated_client, app):
        pricing = finance_factories.CollectivePricingFactory(
            collectiveBooking__collectiveStock__startDatetime=datetime.datetime(1970, 1, 1),
        )
        url = url_for(self.endpoint, collective_offer_id=pricing.collectiveBooking.collectiveStock.collectiveOffer.id)
        app.redis_client.set(finance_conf.REDIS_GENERATE_CASHFLOW_LOCK, "1", 600)
        try:
            with assert_num_queries(4):
                response = authenticated_client.get(url)
                assert response.status_code == 200
        finally:
            app.redis_client.delete(finance_conf.REDIS_GENERATE_CASHFLOW_LOCK)

        assert "Ajuster le prix de l'offre" not in response.data.decode()

    def test_get_validated_offer(self, legit_user, authenticated_client):
        event_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        validation_date = datetime.datetime.utcnow()
        collective_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__startDatetime=event_date,
            collectiveStock__collectiveOffer__lastValidationDate=validation_date,
            collectiveStock__collectiveOffer__validation=offers_models.OfferValidationStatus.APPROVED,
            collectiveStock__collectiveOffer__lastValidationAuthor=legit_user,
        )
        url = url_for(self.endpoint, collective_offer_id=collective_booking.collectiveStock.collectiveOffer.id)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)

        content_as_text = html_parser.content_as_text(response.data)
        assert response.status_code == 200
        assert f"Utilisateur de la dernière validation : {legit_user.full_name}" in content_as_text
        assert f"Date de dernière validation : {format_date(validation_date, '%d/%m/%Y à %Hh%M')}" in content_as_text

    def test_get_rejected_offer(self, legit_user, authenticated_client):
        event_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        validation_date = datetime.datetime.utcnow()
        collective_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__startDatetime=event_date,
            collectiveStock__collectiveOffer__lastValidationDate=validation_date,
            collectiveStock__collectiveOffer__validation=offers_models.OfferValidationStatus.REJECTED,
            collectiveStock__collectiveOffer__lastValidationAuthor=legit_user,
            collectiveStock__collectiveOffer__rejectionReason=educational_models.CollectiveOfferRejectionReason.MISSING_DESCRIPTION,
        )
        url = url_for(self.endpoint, collective_offer_id=collective_booking.collectiveStock.collectiveOffer.id)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        content_as_text = html_parser.content_as_text(response.data)
        assert f"Utilisateur de la dernière validation : {legit_user.full_name}" in content_as_text
        assert f"Date de dernière validation : {format_date(validation_date, '%d/%m/%Y à %Hh%M')}" in content_as_text
        assert "Raison de rejet : Description manquante" in content_as_text

    def test_collective_offer_with_offerer_confidence_rule(self, authenticated_client):
        rule = offerers_factories.ManualReviewOffererConfidenceRuleFactory(offerer__name="Offerer")
        collective_offer = educational_factories.CollectiveOfferFactory(venue__managingOfferer=rule.offerer)

        url = url_for(self.endpoint, collective_offer_id=collective_offer.id)
        with assert_num_queries(self.expected_num_queries_with_ff - 1):  # no _is_collective_offer_price_editable
            response = authenticated_client.get(url)
            assert response.status_code == 200

        text = html_parser.extract_cards_text(response.data)[0]
        assert "Entité juridique : Offerer Revue manuelle" in text

    def test_collective_offer_with_venue_confidence_rule(self, authenticated_client):
        rule = offerers_factories.ManualReviewVenueConfidenceRuleFactory(venue__name="Venue")
        collective_offer = educational_factories.CollectiveOfferFactory(venue=rule.venue)

        url = url_for(self.endpoint, collective_offer_id=collective_offer.id)
        with assert_num_queries(self.expected_num_queries_with_ff - 1):  # no _is_collective_offer_price_editable
            response = authenticated_client.get(url)
            assert response.status_code == 200

        text = html_parser.extract_cards_text(response.data)[0]
        assert "Partenaire culturel : Venue Revue manuelle" in text

    def test_collective_offer_with_top_acteur_offerer(self, authenticated_client):
        collective_offer = educational_factories.CollectiveOfferFactory(
            venue__managingOfferer__name="Offerer",
            venue__managingOfferer__tags=[
                offerers_factories.OffererTagFactory(name="top-acteur", label="Top Acteur"),
                offerers_factories.OffererTagFactory(name="test", label="Test"),
            ],
        )

        url = url_for(self.endpoint, collective_offer_id=collective_offer.id)
        with assert_num_queries(self.expected_num_queries_with_ff - 1):  # no _is_collective_offer_price_editable
            response = authenticated_client.get(url)
            assert response.status_code == 200

        text = html_parser.extract_cards_text(response.data)[0]
        assert "Entité juridique : Offerer Top Acteur" in text


###################################################################
# New tests witj WIP_ENABLE_BO_COLLECTIVE_OFFER_DETAILS_V2 = True #
###################################################################


@pytest.mark.features(WIP_ENABLE_BO_COLLECTIVE_OFFER_DETAILS_V2=True)
class RejectCollectiveOfferFromDetailsButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
    button_label = "Rejeter"
    endpoint = "backoffice_web.collective_offer.get_collective_offer_details"

    @property
    def path(self):
        stock = educational_factories.CollectiveStockFactory()
        return url_for(self.endpoint, collective_offer_id=stock.collectiveOffer.id)


@pytest.mark.features(WIP_ENABLE_BO_COLLECTIVE_OFFER_DETAILS_V2=True)
class ValidateCollectiveOfferFromDetailsButtonTest(button_helpers.ButtonHelper):
    needed_permission = perm_models.Permissions.PRO_FRAUD_ACTIONS
    button_label = "Valider"
    endpoint = "backoffice_web.collective_offer.get_collective_offer_details"

    @property
    def path(self):
        stock = educational_factories.CollectiveStockFactory()
        return url_for(self.endpoint, collective_offer_id=stock.collectiveOffer.id)


@pytest.mark.features(WIP_ENABLE_BO_COLLECTIVE_OFFER_DETAILS_V2=True)
class GetCollectiveOfferDetailTest(GetEndpointHelper):
    endpoint = "backoffice_web.collective_offer.get_collective_offer_details"
    endpoint_kwargs = {"collective_offer_id": 1}
    needed_permission = perm_models.Permissions.READ_OFFERS
    # Use assert_num_queries() instead of assert_no_duplicated_queries() which does not detect one extra query caused
    # by a field added in the jinja template.
    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch CollectiveOffer
    # - _is_collective_offer_price_editable
    expected_num_queries = 4
    expected_num_queries_with_ff = expected_num_queries + 1  # FF MOVE_OFFER_TEST

    def test_nominal(self, legit_user, authenticated_client):
        start_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        end_date = start_date + datetime.timedelta(days=28)
        collective_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__startDatetime=start_date,
            collectiveStock__endDatetime=end_date,
            collectiveStock__collectiveOffer__teacher=educational_factories.EducationalRedactorFactory(
                firstName="Pacôme", lastName="De Champignac"
            ),
            collectiveStock__collectiveOffer__institution=educational_factories.EducationalInstitutionFactory(
                name="Ecole de Marcinelle"
            ),
            collectiveStock__collectiveOffer__template=educational_factories.CollectiveOfferTemplateFactory(
                name="offre Vito Cortizone pour lieu que l'on ne peut refuser"
            ),
        )
        url = url_for(self.endpoint, collective_offer_id=collective_booking.collectiveStock.collectiveOffer.id)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        buttons = html_parser.extract(response.data, "button")
        assert "Ajuster le prix" in buttons

        badges = html_parser.extract_badges(response.data)
        assert "• Validée" in badges

        descriptions = html_parser.extract_descriptions(response.data)
        assert descriptions["Date de l'évènement"] == f"{start_date:%d/%m/%Y} → {end_date:%d/%m/%Y}"
        assert descriptions["Statut"] == "Expirée"
        assert descriptions["Statut PC Pro"] == "Réservée"
        assert "Utilisateur de la dernière validation" not in descriptions
        assert "Date de dernière validation de l’offre" not in descriptions
        assert descriptions["Enseignant"] == "Pacôme De Champignac"
        assert descriptions["Établissement"] == "Ecole de Marcinelle"
        assert descriptions["Offre vitrine liée"] == "offre Vito Cortizone pour lieu que l'on ne peut refuser"

    def test_processed_pricing(self, legit_user, authenticated_client):
        pricing = finance_factories.CollectivePricingFactory(
            status=finance_models.PricingStatus.PROCESSED,
            collectiveBooking__collectiveStock__startDatetime=datetime.datetime(1970, 1, 1),
        )
        url = url_for(self.endpoint, collective_offer_id=pricing.collectiveBooking.collectiveStock.collectiveOffer.id)

        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        buttons = html_parser.extract(response.data, "button")
        assert "Ajuster le prix" not in buttons

    def test_invoiced_pricing(self, legit_user, authenticated_client):
        pricing = finance_factories.CollectivePricingFactory(
            status=finance_models.PricingStatus.INVOICED,
            collectiveBooking__collectiveStock__startDatetime=datetime.datetime(1970, 1, 1),
        )
        url = url_for(self.endpoint, collective_offer_id=pricing.collectiveBooking.collectiveStock.collectiveOffer.id)

        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        buttons = html_parser.extract(response.data, "button")
        assert "Ajuster le prix" not in buttons

    def test_cashflow_pending(self, legit_user, authenticated_client, app):
        pricing = finance_factories.CollectivePricingFactory(
            collectiveBooking__collectiveStock__startDatetime=datetime.datetime(1970, 1, 1),
        )
        url = url_for(self.endpoint, collective_offer_id=pricing.collectiveBooking.collectiveStock.collectiveOffer.id)
        app.redis_client.set(finance_conf.REDIS_GENERATE_CASHFLOW_LOCK, "1", 600)
        try:
            with assert_num_queries(4):
                response = authenticated_client.get(url)
                assert response.status_code == 200
        finally:
            app.redis_client.delete(finance_conf.REDIS_GENERATE_CASHFLOW_LOCK)

        buttons = html_parser.extract(response.data, "button")
        assert "Ajuster le prix" not in buttons

    def test_get_validated_offer(self, legit_user, authenticated_client):
        event_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        validation_date = datetime.datetime.utcnow()
        collective_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__startDatetime=event_date,
            collectiveStock__collectiveOffer__lastValidationDate=validation_date,
            collectiveStock__collectiveOffer__validation=offers_models.OfferValidationStatus.APPROVED,
            collectiveStock__collectiveOffer__lastValidationAuthor=legit_user,
        )
        url = url_for(self.endpoint, collective_offer_id=collective_booking.collectiveStock.collectiveOffer.id)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        descriptions = html_parser.extract_descriptions(response.data)
        assert descriptions["Utilisateur de la dernière validation"] == legit_user.full_name
        assert descriptions["Date de dernière validation"] == format_date(validation_date, "%d/%m/%Y à %Hh%M")

    def test_get_rejected_offer(self, legit_user, authenticated_client):
        event_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        validation_date = datetime.datetime.utcnow()
        collective_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__startDatetime=event_date,
            collectiveStock__collectiveOffer__lastValidationDate=validation_date,
            collectiveStock__collectiveOffer__validation=offers_models.OfferValidationStatus.REJECTED,
            collectiveStock__collectiveOffer__lastValidationAuthor=legit_user,
            collectiveStock__collectiveOffer__rejectionReason=educational_models.CollectiveOfferRejectionReason.MISSING_DESCRIPTION,
        )
        url = url_for(self.endpoint, collective_offer_id=collective_booking.collectiveStock.collectiveOffer.id)
        with assert_num_queries(self.expected_num_queries_with_ff):
            response = authenticated_client.get(url)
            assert response.status_code == 200

        descriptions = html_parser.extract_descriptions(response.data)
        assert descriptions["Utilisateur de la dernière validation"] == legit_user.full_name
        assert descriptions["Date de dernière validation"] == format_date(validation_date, "%d/%m/%Y à %Hh%M")
        assert descriptions["Raison de rejet"] == "Description manquante"

    def test_collective_offer_with_offerer_confidence_rule(self, authenticated_client):
        rule = offerers_factories.ManualReviewOffererConfidenceRuleFactory(offerer__name="Offerer")
        collective_offer = educational_factories.CollectiveOfferFactory(venue__managingOfferer=rule.offerer)

        url = url_for(self.endpoint, collective_offer_id=collective_offer.id)
        with assert_num_queries(self.expected_num_queries_with_ff - 1):  # no _is_collective_offer_price_editable
            response = authenticated_client.get(url)
            assert response.status_code == 200

        descriptions = html_parser.extract_descriptions(response.data)
        assert descriptions["Entité juridique"] == "Offerer Revue manuelle"

    def test_collective_offer_with_venue_confidence_rule(self, authenticated_client):
        rule = offerers_factories.ManualReviewVenueConfidenceRuleFactory(venue__name="Venue")
        collective_offer = educational_factories.CollectiveOfferFactory(venue=rule.venue)

        url = url_for(self.endpoint, collective_offer_id=collective_offer.id)
        with assert_num_queries(self.expected_num_queries_with_ff - 1):  # no _is_collective_offer_price_editable
            response = authenticated_client.get(url)
            assert response.status_code == 200

        descriptions = html_parser.extract_descriptions(response.data)
        assert descriptions["Partenaire culturel"] == "Venue Revue manuelle"

    def test_collective_offer_with_top_acteur_offerer(self, authenticated_client):
        collective_offer = educational_factories.CollectiveOfferFactory(
            venue__managingOfferer__name="Offerer",
            venue__managingOfferer__tags=[
                offerers_factories.OffererTagFactory(name="top-acteur", label="Top Acteur"),
                offerers_factories.OffererTagFactory(name="test", label="Test"),
            ],
        )

        url = url_for(self.endpoint, collective_offer_id=collective_offer.id)
        with assert_num_queries(self.expected_num_queries_with_ff - 1):  # no _is_collective_offer_price_editable
            response = authenticated_client.get(url)
            assert response.status_code == 200

        descriptions = html_parser.extract_descriptions(response.data)
        assert descriptions["Entité juridique"] == "Offerer Top Acteur"

    @pytest.mark.features(MOVE_OFFER_TEST=True)
    def test_move_offer(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)

        url = url_for(self.endpoint, collective_offer_id=collective_offer.id)

        response = authenticated_client.get(url)
        assert response.status_code == 200

        buttons = html_parser.extract(response.data, "button")
        assert "Déplacer l'offre" in buttons
        assert (
            html_parser.get_tag(response.data, tag="div", id=f"move-collective-offer-modal-{collective_offer.id}")
            is not None
        )
