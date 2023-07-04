import copy

import pytest

from pcapi.connectors import beamer
from pcapi.core.external.attributes import models as attributes_models
from pcapi.core.offerers.models import VenueTypeCode
from pcapi.core.testing import override_settings


PRO_ATTRIBUTES = attributes_models.ProAttributes(
    user_id="1",
    dms_application_submitted=True,
    dms_application_approved=True,
    has_bookings=False,
    has_offers=False,
    has_individual_offers=False,
    is_booking_email=True,
    is_eac=True,
    isPermanent=True,
    is_pro=True,
    isVirtual=False,
    offerers_names=["offerer name 1", "offerer name 2"],
    user_is_attached=True,
    venues_labels=["venue label 1", "venue label 2"],
    venues_types=[VenueTypeCode.MUSEUM.name, VenueTypeCode.TRAVELING_CINEMA.name],
    is_user_email=True,
    marketing_email_subscription=True,
    offerers_tags=["offerer tag 1", "offerer tag 2"],
    venues_ids=[2, 3],
    venues_names=["venue name 1", "venue name 2"],
    postal_code="75008",
    departement_code="75",
)
BEAMER_ATTRIBUTES = {
    "userId": "1",
    "DMS_APPLICATION_SUBMITTED": True,
    "DMS_APPLICATION_APPROVED": True,
    "HAS_BOOKINGS": False,
    "HAS_OFFERS": False,
    "HAS_INDIVIDUAL_OFFERS": False,
    "IS_BOOKING_EMAIL": True,
    "IS_EAC": True,
    "IS_PERMANENT": True,
    "IS_PRO": True,
    "IS_VIRTUAL": False,
    "OFFERER_NAME": "offerer name 1;offerer name 2",
    "USER_IS_ATTACHED": True,
    "VENUE_LABEL": "venue label 1;venue label 2",
    "VENUE_TYPE": f"{VenueTypeCode.MUSEUM.name};{VenueTypeCode.TRAVELING_CINEMA.name}",
}


def test_beamer_attributes_format():
    assert BEAMER_ATTRIBUTES == beamer.format_pro_attributes(PRO_ATTRIBUTES)


@override_settings(BEAMER_BACKEND="pcapi.connectors.beamer.BeamerBackend")
class BeamerConnectorTest:
    def test_beamer_attributes(self, requests_mock):
        requests_mock.put("https://api.getbeamer.com/v0/users")

        beamer.update_beamer_user(PRO_ATTRIBUTES)

        assert requests_mock.last_request.json() == BEAMER_ATTRIBUTES

    def test_user_id_missing(self):
        pro_attributes_with_no_id = copy.deepcopy(PRO_ATTRIBUTES)
        pro_attributes_with_no_id.user_id = ""

        with pytest.raises(beamer.MissingIdException):
            beamer.update_beamer_user(pro_attributes_with_no_id)

    def test_error_handling(self, requests_mock):
        requests_mock.put("https://api.getbeamer.com/v0/users", status_code=403)

        with pytest.raises(beamer.BeamerException):
            beamer.update_beamer_user(PRO_ATTRIBUTES)
