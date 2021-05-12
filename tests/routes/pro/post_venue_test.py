import pytest

from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue_label
from pcapi.model_creators.generic_creators import create_venue_type
from pcapi.models import Venue
from pcapi.repository import repository
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Post:
    class Returns201:
        @pytest.mark.usefixtures("db_session")
        def test_should_register_new_venue(self, app):
            # given
            offerer = create_offerer(siren="302559178")
            user = create_user()
            user_offerer = create_user_offerer(user, offerer)
            venue_type = create_venue_type(label="Musée")
            venue_label = create_venue_label(label="CAC - Centre d'art contemporain d'intérêt national")
            repository.save(user_offerer, venue_type, venue_label)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)
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

        @pytest.mark.usefixtures("db_session")
        def test_should_consider_the_venue_to_be_permanent(self, app):
            # given
            offerer = create_offerer(siren="302559178")
            user = create_user()
            user_offerer = create_user_offerer(user, offerer)
            venue_type = create_venue_type(label="Musée")
            venue_label = create_venue_label(label="CAC - Centre d'art contemporain d'intérêt national")
            repository.save(user_offerer, venue_type, venue_label)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)
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

    class Returns400:
        @pytest.mark.usefixtures("db_session")
        def when_latitude_out_of_range_and_longitude_wrong_format(self, app):
            # given
            offerer = create_offerer(siren="302559178")
            user = create_user()
            user_offerer = create_user_offerer(user, offerer)
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

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.post("/venues", json=data)

            # then
            assert response.status_code == 400
            assert response.json["latitude"] == ["La latitude doit être comprise entre -90.0 et +90.0"]
            assert response.json["longitude"] == ["Format incorrect"]

        @pytest.mark.usefixtures("db_session")
        def when_longitude_out_of_range_and_latitude_wrong_format(self, app):
            # given
            offerer = create_offerer(siren="302559178")
            user = create_user()
            user_offerer = create_user_offerer(user, offerer)
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

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.post("/venues", json=data)

            # then
            assert response.status_code == 400
            assert response.json["longitude"] == ["La longitude doit être comprise entre -180.0 et +180.0"]
            assert response.json["latitude"] == ["Format incorrect"]
