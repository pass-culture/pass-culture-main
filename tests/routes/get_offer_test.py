from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, \
    create_offerer, \
    create_user, \
    create_venue, create_offer_with_thing_product, create_bank_information, create_stock
from utils.human_ids import humanize


class Get:
    class Returns200:
        @clean_database
        def when_user_has_rights_on_managing_offerer(self, app):
            # Given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            stock = create_stock(offer=offer)
            create_bank_information(venue=venue, id_at_providers=venue.siret)
            create_bank_information(offerer=offerer, id_at_providers=offerer.siren)

            PcObject.save(user, stock)

            # when
            response = TestClient().with_auth(email='user@test.com')\
                .get(API_URL + f'/offers/{humanize(offer.id)}')

            # then
            response_json = response.json()
            assert response.status_code == 200
            assert 'iban' in response_json['venue']
            assert 'bic' in response_json['venue']
            assert 'iban' in response_json['venue']['managingOfferer']
            assert 'bic' in response_json['venue']['managingOfferer']
