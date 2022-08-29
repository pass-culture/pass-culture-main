import datetime

import pytest

from pcapi.core import testing
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
    offerers_factories.VenueFactory(managingOfferer=offerer, withdrawalDetails="More venue withdrawal details")
    offerers_factories.ApiKeyFactory(offerer=offerer, prefix="testenv_prefix")
    offerers_factories.ApiKeyFactory(offerer=offerer, prefix="testenv_prefix2")
    finance_factories.BankInformationFactory(venue=venue_1, applicationId=2, status="REJECTED")
    finance_factories.BankInformationFactory(venue=venue_1, applicationId=3)
    finance_factories.BankInformationFactory(venue=venue_2, applicationId=4)

    offerer_id = offerer.id
    client = client.with_session_auth(pro.email)
    db.session.commit()
    n_queries = (
        testing.AUTHENTICATION_QUERIES
        + 1  # check_user_has_access_to_offerer
        + 1  # Offerer
        + 1  # Offerer api_key prefix
        + 1  # venues (manual with joinedload)
        + 1  # Offerer hasDigitalVenueAtLeastOneOffer
        + 1  # Offerer BankInformation
        + 1  # Offerer hasMissingBankInformation
        + 1  # Offerer.managedVenues (automatic by Pydantic)
    )
    with testing.assert_num_queries(n_queries):
        response = client.get(f"/offerers/{humanize(offerer_id)}")

    expected_serialized_offerer = {
        "address": offerer.address,
        "apiKey": {"maxAllowed": 5, "prefixes": ["testenv_prefix", "testenv_prefix2"]},
        "bic": None,
        "iban": None,
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
                "audioDisabilityCompliant": False,
                "address": venue.address,
                "bookingEmail": venue.bookingEmail,
                "businessUnitId": venue.businessUnitId,
                "city": venue.city,
                "comment": venue.comment,
                "departementCode": venue.departementCode,
                "hasMissingReimbursementPoint": venue.hasMissingReimbursementPoint,
                "id": humanize(venue.id),
                "isValidated": venue.isValidated,
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
            for venue in offerer.managedVenues
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
    response = client.get(f"/offerers/{humanize(offerer.id)}")

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

    response = client.get(f"/offerers/{humanize(offerer_id)}")
    assert response.status_code == 200
    assert response.json["managedVenues"][0]["hasMissingReimbursementPoint"] == True
    assert response.json["managedVenues"][1]["hasMissingReimbursementPoint"] == False
    assert response.json["managedVenues"][2]["hasMissingReimbursementPoint"] == False
