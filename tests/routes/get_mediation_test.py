import pytest

from pcapi.model_creators.generic_creators import create_user, \
    create_offerer, \
    create_venue, \
    create_user_offerer, \
    create_mediation, \
    create_provider
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.repository import repository
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize
from tests.conftest import TestClient


class Get:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_the_mediation_exists(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user_offerer = create_user_offerer(user, offerer)
            provider = create_provider(local_class='TestLocalProvider', idx=134)
            mediation = create_mediation(offer, last_provider_id=provider.id, id_at_providers='VHBZJQ',
                                         credit='Mickael Bay')
            repository.save(provider, mediation)
            repository.save(offer)
            repository.save(user, venue, offerer, user_offerer)

            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.get('/mediations/%s' % humanize(mediation.id))

            # then
            assert response.status_code == 200
            assert response.json == {
                'authorId': None,
                'credit': 'Mickael Bay',
                'dateCreated': format_into_utc_date(mediation.dateCreated),
                'dateModifiedAtLastProvider': format_into_utc_date(mediation.dateModifiedAtLastProvider),
                'fieldsUpdated': [],
                'id': humanize(mediation.id),
                'idAtProviders': 'VHBZJQ',
                'isActive': True,
                'lastProviderId': humanize(134),
                'offerId': humanize(offer.id),
                'thumbCount': 0
            }

    class Returns404:
        @pytest.mark.usefixtures("db_session")
        def when_the_mediation_does_not_exist(self, app):
            # given
            user = create_user()
            repository.save(user)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.get('/mediations/AE')

            # then
            assert response.status_code == 404
            assert response.json == {}
