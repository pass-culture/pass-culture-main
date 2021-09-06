import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.users.factories import ProFactory
from pcapi.models import Venue
from pcapi.repository import repository
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
def test_should_register_new_venue(app):
    # given
    offerer = offers_factories.OffererFactory(siren="302559178")
    user = ProFactory()
    user_offerer = offers_factories.UserOffererFactory(user=user, offerer=offerer)
    venue_type = offerers_factories.VenueTypeFactory(label="Musée")
    venue_label = offerers_factories.VenueLabelFactory(label="CAC - Centre d'art contemporain d'intérêt national")
    repository.save(user_offerer, venue_type, venue_label)
    auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)
    venue_data = {
        "name": "Ma venue",
        "siret": "30255917810045",
        "address": "75 Rue Charles Fourier, 75013 Paris",
        "postalCode": "75200",
        "bookingEmail": "toto@example.com",
        "city": "Paris",
        "managingOffererId": humanize(offerer.id),
        "latitude": 48.82387,
        "longitude": 2.35284,
        "publicName": "Ma venue publique",
        "venueTypeId": humanize(venue_type.id),
        "venueLabelId": humanize(venue_label.id),
        "description": "Some description",
        "audioDisabilityCompliant": True,
        "contact": {"email": "some@email.com"},
    }

    # when
    response = auth_request.post("/venues", json=venue_data)

    # then
    assert response.status_code == 201
    idx = response.json["id"]

    venue = Venue.query.filter_by(id=dehumanize(idx)).one()
    assert venue.name == "Ma venue"
    assert venue.publicName == "Ma venue publique"
    assert venue.siret == "30255917810045"
    assert venue.isValidated
    assert venue.venueTypeId == venue_type.id
    assert venue.venueLabelId == venue_label.id
    assert venue.description == "Some description"
    assert venue.audioDisabilityCompliant
    assert venue.contact.email == "some@email.com"
    assert not venue.contact.phone_number
    assert not venue.contact.social_medias


@pytest.mark.usefixtures("db_session")
def test_should_consider_the_venue_to_be_permanent(app):
    # given
    offerer = offers_factories.OffererFactory(siren="302559178")
    user = ProFactory()
    user_offerer = offers_factories.UserOffererFactory(user=user, offerer=offerer)
    venue_type = offerers_factories.VenueTypeFactory(label="Musée")
    venue_label = offerers_factories.VenueLabelFactory(label="CAC - Centre d'art contemporain d'intérêt national")
    repository.save(user_offerer, venue_type, venue_label)
    auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)
    venue_data = {
        "name": "Ma venue",
        "siret": "30255917810045",
        "address": "75 Rue Charles Fourier, 75013 Paris",
        "postalCode": "75200",
        "bookingEmail": "toto@example.com",
        "city": "Paris",
        "managingOffererId": humanize(offerer.id),
        "latitude": 48.82387,
        "longitude": 2.35284,
        "publicName": "Ma venue publique",
        "venueTypeId": humanize(venue_type.id),
        "venueLabelId": humanize(venue_label.id),
    }

    # when
    auth_request.post("/venues", json=venue_data)

    # then
    venue = Venue.query.one()
    assert venue.isPermanent == True


@pytest.mark.usefixtures("db_session")
def test_should_return_401_when_latitude_out_of_range_and_longitude_wrong_format(app):
    # given
    offerer = offers_factories.OffererFactory(siren="302559178")
    user = ProFactory()
    user_offerer = offers_factories.UserOffererFactory(user=user, offerer=offerer)
    repository.save(user_offerer)

    data = {
        "name": "Ma venue",
        "siret": "30255917810045",
        "address": "75 Rue Charles Fourier, 75013 Paris",
        "postalCode": "75200",
        "bookingEmail": "toto@example.com",
        "city": "Paris",
        "managingOffererId": humanize(offerer.id),
        "latitude": -98.82387,
        "longitude": "112°3534",
    }

    auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

    # when
    response = auth_request.post("/venues", json=data)

    # then
    assert response.status_code == 400
    assert response.json["latitude"] == ["La latitude doit être comprise entre -90.0 et +90.0"]
    assert response.json["longitude"] == ["Format incorrect"]


@pytest.mark.usefixtures("db_session")
def test_should_return_401_when_longitude_out_of_range_and_latitude_wrong_format(app):
    # given
    offerer = offers_factories.OffererFactory(siren="302559178")
    user = ProFactory()
    user_offerer = offers_factories.UserOffererFactory(user=user, offerer=offerer)
    repository.save(user_offerer)

    data = {
        "name": "Ma venue",
        "siret": "30255917810045",
        "address": "75 Rue Charles Fourier, 75013 Paris",
        "postalCode": "75200",
        "bookingEmail": "toto@example.com",
        "city": "Paris",
        "managingOffererId": humanize(offerer.id),
        "latitude": "76°8237",
        "longitude": 210.43251,
    }

    auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

    # when
    response = auth_request.post("/venues", json=data)

    # then
    assert response.status_code == 400
    assert response.json["longitude"] == ["La longitude doit être comprise entre -180.0 et +180.0"]
    assert response.json["latitude"] == ["Format incorrect"]


@pytest.mark.usefixtures("db_session")
def test_should_return_403_when_user_is_not_managing_offerer_create_venue(app):
    offerer = offers_factories.OffererFactory(siren="302559178")
    user = ProFactory()
    venue_type = offerers_factories.VenueTypeFactory(label="Musée")
    venue_data = {
        "name": "Ma venue",
        "siret": "30255917810045",
        "address": "75 Rue Charles Fourier, 75013 Paris",
        "postalCode": "75200",
        "bookingEmail": "toto@example.com",
        "city": "Paris",
        "managingOffererId": humanize(offerer.id),
        "latitude": 48.82387,
        "longitude": 2.35284,
        "publicName": "Ma venue publique",
        "venueTypeId": humanize(venue_type.id),
    }
    auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

    response = auth_request.post("/venues", json=venue_data)

    assert response.status_code == 403
    assert response.json["global"] == ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]


venue_malformed_test_data = [
    ({"description": "a" * 1024}, "description"),
    ({"contact": {"email": "not_an_email"}}, "contact.email"),
    ({"contact": {"website": "not_an_url"}}, "contact.website"),
    ({"contact": {"phoneNumber": "not_a_phone_number"}}, "contact.phoneNumber"),
    ({"contact": {"social_medias": {"a": "b"}}}, "contact.socialMedias.__key__"),
    ({"contact": {"social_medias": {"facebook": "not_an_url"}}}, "contact.socialMedias.facebook"),
]


@pytest.mark.usefixtures("db_session")
@pytest.mark.parametrize("data, key", venue_malformed_test_data)
def test_create_venue_malformed(app, client, data, key):
    user_offerer = offers_factories.UserOffererFactory()

    client = client.with_session_auth(user_offerer.user.email)
    response = client.post("/venues", json=data)

    assert response.status_code == 400
    assert key in response.json
