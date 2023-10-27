import datetime

import pytest

from pcapi.core import testing
import pcapi.core.educational.factories as collective_factories
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import db
from pcapi.utils.date import format_into_utc_date


class GetOffererTest:
    @pytest.mark.usefixtures("db_session")
    def test_basics(self, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        venue_1 = offerers_factories.VenueFactory(managingOfferer=offerer, withdrawalDetails="Venue withdrawal details")
        offers_factories.OfferFactory(venue=venue_1)
        offerers_factories.VenueReimbursementPointLinkFactory(venue=venue_1, reimbursementPoint=venue_1)
        venue_2 = offerers_factories.VenueFactory(
            managingOfferer=offerer, withdrawalDetails="Other venue withdrawal details"
        )
        offerers_factories.VenueReimbursementPointLinkFactory(
            venue=venue_2,
            reimbursementPoint=venue_2,
            # old, inactive link
            timespan=[
                datetime.datetime.utcnow() - datetime.timedelta(days=10),
                datetime.datetime.utcnow() - datetime.timedelta(days=9),
            ],
        )
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            withdrawalDetails="More venue withdrawal details",
            adageId="123",
            adageInscriptionDate=datetime.datetime.utcnow(),
        )
        collective_factories.CollectiveDmsApplicationFactory(
            venue=venue,
        )
        offerers_factories.ApiKeyFactory(offerer=offerer, prefix="testenv_prefix")
        offerers_factories.ApiKeyFactory(offerer=offerer, prefix="testenv_prefix2")
        finance_factories.BankInformationFactory(venue=venue_1, applicationId=2, status="REJECTED")
        finance_factories.BankInformationFactory(venue=venue_1, applicationId=3)
        finance_factories.BankInformationFactory(venue=venue_2, applicationId=4)

        offerer_id = offerer.id
        client = client.with_session_auth(pro.email)
        db.session.commit()

        with testing.assert_no_duplicated_queries():
            response = client.get(f"/offerers/{offerer_id}")

        expected_serialized_offerer = {
            "address": offerer.address,
            "apiKey": {"maxAllowed": 5, "prefixes": ["testenv_prefix", "testenv_prefix2"]},
            "city": offerer.city,
            "dateCreated": format_into_utc_date(offerer.dateCreated),
            "demarchesSimplifieesApplicationId": None,
            "hasAvailablePricingPoints": True,
            "hasDigitalVenueAtLeastOneOffer": False,
            "hasValidBankAccount": False,
            "hasPendingBankAccount": False,
            "venuesWithNonFreeOffersWithoutBankAccounts": [],
            "isActive": offerer.isActive,
            "isValidated": offerer.isValidated,
            "managedVenues": [
                {
                    "adageInscriptionDate": format_into_utc_date(venue.adageInscriptionDate)
                    if venue.adageInscriptionDate
                    else None,
                    "address": venue.address,
                    "audioDisabilityCompliant": False,
                    "bookingEmail": venue.bookingEmail,
                    "city": venue.city,
                    "collectiveDmsApplications": [
                        {
                            "venueId": a.venue.id,
                            "state": a.state,
                            "procedure": a.procedure,
                            "application": a.application,
                            "lastChangeDate": format_into_utc_date(a.lastChangeDate),
                            "depositDate": format_into_utc_date(a.depositDate),
                            "expirationDate": format_into_utc_date(a.expirationDate) if a.expirationDate else None,
                            "buildDate": format_into_utc_date(a.buildDate) if a.buildDate else None,
                            "instructionDate": format_into_utc_date(a.instructionDate) if a.instructionDate else None,
                            "processingDate": format_into_utc_date(a.processingDate) if a.processingDate else None,
                            "userDeletionDate": format_into_utc_date(a.userDeletionDate)
                            if a.userDeletionDate
                            else None,
                        }
                        for a in venue.collectiveDmsApplications
                    ],
                    "comment": venue.comment,
                    "demarchesSimplifieesApplicationId": venue.demarchesSimplifieesApplicationId,
                    "departementCode": venue.departementCode,
                    "hasAdageId": bool(venue.adageId),
                    "hasMissingReimbursementPoint": venue.hasMissingReimbursementPoint,
                    "hasPendingBankInformationApplication": venue.hasPendingBankInformationApplication,
                    "hasCreatedOffer": venue.has_individual_offers or venue.has_collective_offers,
                    "isVirtual": venue.isVirtual,
                    "mentalDisabilityCompliant": False,
                    "motorDisabilityCompliant": False,
                    "name": venue.name,
                    "id": venue.id,
                    "postalCode": venue.postalCode,
                    "publicName": venue.publicName,
                    "siret": venue.siret,
                    "venueTypeCode": venue.venueTypeCode.name,
                    "visualDisabilityCompliant": False,
                    "withdrawalDetails": venue.withdrawalDetails,
                    "hasVenueProviders": False,
                }
                for venue in sorted(offerer.managedVenues, key=lambda v: v.publicName)
            ],
            "name": offerer.name,
            "id": offerer.id,
            "postalCode": offerer.postalCode,
            "siren": offerer.siren,
            "dsToken": offerer.dsToken,
        }
        assert response.status_code == 200
        assert response.json == expected_serialized_offerer

        db.session.refresh(offerer)
        assert len(offerer.managedVenues) == 3

    @pytest.mark.usefixtures("db_session")
    def test_unknown_offerer(self, client):
        pro = users_factories.ProFactory()

        client = client.with_session_auth(pro.email)
        response = client.get("/offerers/ABC1234")

        assert response.status_code == 404

    @pytest.mark.usefixtures("db_session")
    def test_unauthorized_offerer(self, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()

        client = client.with_session_auth(pro.email)
        response = client.get(f"/offerers/{offerer.id}")

        assert response.status_code == 403

    @pytest.mark.usefixtures("db_session")
    def test_serialize_venue_has_missing_reimbursement_point(self, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        offerers_factories.VenueFactory(
            managingOfferer=offerer, reimbursement_point=None, name="A - Venue without reimbursement point"
        )
        venue_with_pending_application = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            reimbursement_point=None,
            name="B - Venue without reimbursement point with pending application",
        )
        finance_factories.BankInformationFactory(venue=venue_with_pending_application, applicationId=4, status="DRAFT")
        offerers_factories.VenueFactory(
            managingOfferer=offerer, name="C - Venue with reimbursement point", reimbursement_point="self"
        )

        offerer_id = offerer.id
        client = client.with_session_auth(pro.email)

        response = client.get(f"/offerers/{offerer_id}")
        assert response.status_code == 200
        assert response.json["managedVenues"][0]["hasMissingReimbursementPoint"] is True
        assert response.json["managedVenues"][1]["hasMissingReimbursementPoint"] is False
        assert response.json["managedVenues"][2]["hasMissingReimbursementPoint"] is False
        assert response.json["hasValidBankAccount"] is False
        assert response.json["hasPendingBankAccount"] is False
        assert response.json["venuesWithNonFreeOffersWithoutBankAccounts"] == []

    @pytest.mark.usefixtures("db_session")
    def test_serialize_venue_offer_created_flag(self, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        venue_with_offer = offerers_factories.VenueFactory(managingOfferer=offerer)
        offers_factories.OfferFactory(venue=venue_with_offer)

        venue_with_collective_offer = offerers_factories.VenueFactory(managingOfferer=offerer)
        collective_factories.CollectiveOfferFactory(venue=venue_with_collective_offer)

        venue_with_collective_offer_template = offerers_factories.VenueFactory(managingOfferer=offerer)
        collective_factories.CollectiveOfferTemplateFactory(venue=venue_with_collective_offer_template)

        offerers_factories.VenueFactory(managingOfferer=offerer)

        offerer_id = offerer.id
        client = client.with_session_auth(pro.email)

        response = client.get(f"/offerers/{offerer_id}")
        assert response.status_code == 200
        assert response.json["managedVenues"][0]["hasCreatedOffer"] is True
        assert response.json["managedVenues"][1]["hasCreatedOffer"] is True
        assert response.json["managedVenues"][2]["hasCreatedOffer"] is True
        assert response.json["managedVenues"][3]["hasCreatedOffer"] is False
        assert response.json["hasValidBankAccount"] is False
        assert response.json["hasPendingBankAccount"] is False
        assert response.json["venuesWithNonFreeOffersWithoutBankAccounts"] == []

    @pytest.mark.usefixtures("db_session")
    def test_we_dont_display_anything_if_offerer_dont_have_any_bank_accounts_nor_venues(self, client):
        # Given
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        # When
        http_client = client.with_session_auth(pro_user.email)

        response = http_client.get(f"/offerers/{offerer.id}")

        # Then
        assert response.status_code == 200
        offerer = response.json

        assert offerer["hasValidBankAccount"] is False
        assert offerer["hasPendingBankAccount"] is False
        assert offerer["venuesWithNonFreeOffersWithoutBankAccounts"] == []

    @pytest.mark.usefixtures("db_session")
    def test_client_can_now_if_the_offerer_have_any_valid_bank_account(self, client):
        # Given
        _another_pro_user = users_factories.ProFactory()
        another_offerer = offerers_factories.OffererFactory()
        another_bank_account = finance_factories.BankAccountFactory(offerer=another_offerer)
        another_venue = offerers_factories.VenueFactory(managingOfferer=another_offerer)
        _another_link = offerers_factories.VenueBankAccountLinkFactory(
            venue=another_venue, bankAccount=another_bank_account
        )

        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)
        offerers_factories.VenueWithoutSiretFactory(managingOfferer=offerer)
        finance_factories.BankAccountFactory(offerer=offerer)

        # When
        http_client = client.with_session_auth(pro_user.email)

        response = http_client.get(f"/offerers/{offerer.id}")

        # Then
        assert response.status_code == 200
        offerer = response.json

        assert offerer["hasValidBankAccount"] is True
        assert offerer["hasPendingBankAccount"] is False
        assert offerer["venuesWithNonFreeOffersWithoutBankAccounts"] == []

    @pytest.mark.usefixtures("db_session")
    def test_client_can_know_which_venues_have_non_free_offers_without_bank_accounts(self, client):
        # Given
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        expected_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_linked = offerers_factories.VenueFactory(managingOfferer=offerer)
        old_linked_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        non_linked_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        non_linked_venue_with_free_collective_offer = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_linked_offer = offers_factories.OfferFactory(venue=venue_linked)
        old_linked_venue_offer = offers_factories.OfferFactory(venue=old_linked_venue)
        non_linked_venue_offer = offers_factories.OfferFactory(venue=non_linked_venue)
        free_collective_offer = collective_factories.CollectiveOfferFactory(
            venue=non_linked_venue_with_free_collective_offer
        )
        offers_factories.StockFactory(offer=venue_linked_offer)
        offers_factories.StockFactory(offer=non_linked_venue_offer)
        offers_factories.StockFactory(offer=old_linked_venue_offer)
        collective_factories.CollectiveStockFactory(collectiveOffer=free_collective_offer, price=0)
        expected_bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        _up_to_date_link = offerers_factories.VenueBankAccountLinkFactory(
            venueId=venue_linked.id,
            bankAccountId=expected_bank_account.id,
            timespan=(datetime.datetime.utcnow(), None),
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venueId=expected_venue.id, bankAccountId=expected_bank_account.id, timespan=(datetime.datetime.utcnow(),)
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venueId=non_linked_venue.id,
            bankAccountId=expected_bank_account.id,
            timespan=(
                datetime.datetime.utcnow() - datetime.timedelta(days=365),
                datetime.datetime.utcnow() - datetime.timedelta(days=10),
            ),
        )

        # When
        http_client = client.with_session_auth(pro_user.email)

        response = http_client.get(f"/offerers/{offerer.id}")

        # Then
        assert response.status_code == 200
        offerer = response.json

        assert offerer["hasValidBankAccount"] is True
        assert offerer["hasPendingBankAccount"] is False
        assert sorted(offerer["venuesWithNonFreeOffersWithoutBankAccounts"]) == [
            old_linked_venue.id,
            non_linked_venue.id,
        ]

    @pytest.mark.usefixtures("db_session")
    def test_client_can_know_if_offerer_have_any_pending_bank_accounts(self, client):
        # Given
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        _refused_bank_account = finance_factories.BankAccountFactory(
            offerer=offerer, status=finance_models.BankAccountApplicationStatus.REFUSED
        )
        _without_continuation_bank_account = finance_factories.BankAccountFactory(
            offerer=offerer, status=finance_models.BankAccountApplicationStatus.REFUSED
        )
        finance_factories.BankAccountFactory(
            offerer=offerer, status=finance_models.BankAccountApplicationStatus.ON_GOING
        )
        # When
        http_client = client.with_session_auth(pro_user.email)

        response = http_client.get(f"/offerers/{offerer.id}")

        # Then
        assert response.status_code == 200
        offerer = response.json

        assert offerer["hasValidBankAccount"] is False
        assert offerer["hasPendingBankAccount"] is True
        assert offerer["venuesWithNonFreeOffersWithoutBankAccounts"] == []

    @pytest.mark.usefixtures("db_session")
    def test_client_can_know_which_venues_have_non_free_offers_without_bank_accounts_taking_collective_offer_into_account(
        self, client
    ):
        # Given
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        expected_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_linked = offerers_factories.VenueFactory(managingOfferer=offerer)
        non_linked_venue_with_collective_offer = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_linked_offer = offers_factories.OfferFactory(venue=venue_linked)
        collective_offer = collective_factories.CollectiveOfferFactory(venue=non_linked_venue_with_collective_offer)
        offers_factories.StockFactory(offer=venue_linked_offer)
        collective_factories.CollectiveStockFactory(collectiveOffer=collective_offer)
        expected_bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        _up_to_date_link = offerers_factories.VenueBankAccountLinkFactory(
            venueId=venue_linked.id,
            bankAccountId=expected_bank_account.id,
            timespan=(datetime.datetime.utcnow(), None),
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venueId=expected_venue.id, bankAccountId=expected_bank_account.id, timespan=(datetime.datetime.utcnow(),)
        )

        # When
        http_client = client.with_session_auth(pro_user.email)

        response = http_client.get(f"/offerers/{offerer.id}")

        # Then
        assert response.status_code == 200
        offerer = response.json

        assert offerer["hasValidBankAccount"] is True
        assert offerer["hasPendingBankAccount"] is False
        assert sorted(offerer["venuesWithNonFreeOffersWithoutBankAccounts"]) == [
            non_linked_venue_with_collective_offer.id,
        ]

    @pytest.mark.usefixtures("db_session")
    def test_user_can_know_if_each_managed_venues_has_venue_provider(self, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        offerers_factories.VenueFactory(managingOfferer=offerer, name="Without venueProvider")
        venue_with_providers = offerers_factories.VenueFactory(managingOfferer=offerer, name="With venueProvider")
        providers_factories.VenueProviderFactory(venue=venue_with_providers)

        offerer_id = offerer.id
        client = client.with_session_auth(pro.email)

        response = client.get(f"/offerers/{offerer_id}")
        assert response.status_code == 200
        assert response.json["managedVenues"][0]["hasVenueProviders"] is False
        assert response.json["managedVenues"][1]["hasVenueProviders"] is True
        assert response.json["hasValidBankAccount"] is False
        assert response.json["hasPendingBankAccount"] is False
        assert response.json["venuesWithNonFreeOffersWithoutBankAccounts"] == []
