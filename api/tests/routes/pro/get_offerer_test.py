import datetime

import pytest

from pcapi.core import testing
import pcapi.core.educational.factories as collective_factories
import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import db
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


def test_basics(client):
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
        "dateModifiedAtLastProvider": format_into_utc_date(offerer.dateModifiedAtLastProvider),
        "demarchesSimplifieesApplicationId": None,
        "hasAvailablePricingPoints": True,
        "hasDigitalVenueAtLeastOneOffer": False,
        "fieldsUpdated": offerer.fieldsUpdated,
        "hasMissingBankInformation": True,
        "id": humanize(offerer.id),
        "idAtProviders": offerer.idAtProviders,
        "isActive": offerer.isActive,
        "isValidated": offerer.isValidated,
        "lastProviderId": offerer.lastProviderId,
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
                        "venueId": a.venueId,
                        "state": a.state,
                        "procedure": a.procedure,
                        "application": a.application,
                        "lastChangeDate": format_into_utc_date(a.lastChangeDate),
                        "depositDate": format_into_utc_date(a.depositDate),
                        "expirationDate": format_into_utc_date(a.expirationDate) if a.expirationDate else None,
                        "buildDate": format_into_utc_date(a.buildDate) if a.buildDate else None,
                        "instructionDate": format_into_utc_date(a.instructionDate) if a.instructionDate else None,
                        "processingDate": format_into_utc_date(a.processingDate) if a.processingDate else None,
                        "userDeletionDate": format_into_utc_date(a.userDeletionDate) if a.userDeletionDate else None,
                    }
                    for a in venue.collectiveDmsApplications
                ],
                "comment": venue.comment,
                "departementCode": venue.departementCode,
                "hasAdageId": bool(venue.adageId),
                "hasMissingReimbursementPoint": venue.hasMissingReimbursementPoint,
                "hasCreatedOffer": venue.has_individual_offers or venue.has_collective_offers,
                "id": humanize(venue.id),
                "isVirtual": venue.isVirtual,
                "managingOffererId": humanize(venue.managingOffererId),
                "mentalDisabilityCompliant": False,
                "motorDisabilityCompliant": False,
                "name": venue.name,
                "nonHumanizedId": venue.id,
                "postalCode": venue.postalCode,
                "publicName": venue.publicName,
                "siret": venue.siret,
                "venueLabelId": humanize(venue.venueLabelId),
                "venueTypeCode": venue.venueTypeCode.name,
                "visualDisabilityCompliant": False,
                "withdrawalDetails": venue.withdrawalDetails,
            }
            for venue in sorted(offerer.managedVenues, key=lambda v: v.publicName)
        ],
        "name": offerer.name,
        "nonHumanizedId": offerer.id,
        "postalCode": offerer.postalCode,
        "siren": offerer.siren,
    }
    assert response.status_code == 200
    assert response.json == expected_serialized_offerer

    db.session.refresh(offerer)
    assert len(offerer.managedVenues) == 3


def test_unknown_offerer(client):
    pro = users_factories.ProFactory()

    client = client.with_session_auth(pro.email)
    response = client.get("/offerers/ABC1234")

    assert response.status_code == 404


def test_unauthorized_offerer(client):
    pro = users_factories.ProFactory()
    offerer = offerers_factories.OffererFactory()

    client = client.with_session_auth(pro.email)
    response = client.get(f"/offerers/{offerer.id}")

    assert response.status_code == 403


def test_serialize_venue_has_missing_reimbursement_point(client):
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
    assert response.json["managedVenues"][0]["hasMissingReimbursementPoint"] == True
    assert response.json["managedVenues"][1]["hasMissingReimbursementPoint"] == False
    assert response.json["managedVenues"][2]["hasMissingReimbursementPoint"] == False


def test_serialize_venue_offer_created_flag(client):
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
    assert response.json["managedVenues"][0]["hasCreatedOffer"] == True
    assert response.json["managedVenues"][1]["hasCreatedOffer"] == True
    assert response.json["managedVenues"][2]["hasCreatedOffer"] == True
    assert response.json["managedVenues"][3]["hasCreatedOffer"] == False
