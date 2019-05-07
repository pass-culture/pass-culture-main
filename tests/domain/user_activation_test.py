from domain.user_activation import generate_activation_users_csv
from models import ThingType
from models.booking import ActivationUser
from tests.test_utils import create_booking, create_user, create_stock, create_offer_with_thing_product, create_venue, create_offerer


class GenerateActivationUsersCsvTest:
    def test_generate_activation_users_csv(self):
        # Given
        user1 = create_user(first_name='Pedro', last_name='Gutierrez', email='email1@test.com',
                            reset_password_token='AZERTY123')
        user2 = create_user(first_name='Pablo', last_name='Rodriguez', email='email2+alias@test.com',
                            reset_password_token='123AZERTY')
        offerer = create_offerer()
        venue = create_venue(offerer, is_virtual=True, address=None, postal_code=None, departement_code=None)
        activation_offer = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        stock = create_stock(offer=activation_offer, price=0)
        booking1 = create_booking(user1, stock, token='abc')
        booking2 = create_booking(user2, stock, token='def')
        bookings = [booking1, booking2]
        activation_users = map(lambda b: ActivationUser(b), bookings)

        # When
        csv = generate_activation_users_csv(activation_users)

        # Then
        csv_list_format = [row.split(',') for row in csv.split('\r\n')]
        csv_list_format = [row_list for row_list in csv_list_format if row_list[0]]
        assert csv_list_format[0] == ['"Prénom"', '"Nom"', '"Email"', '"Contremarque d\'activation"']
        assert csv_list_format[1] == ['"Pedro"', '"Gutierrez"', '"email1@test.com"', '"abc"']
        assert csv_list_format[2] == ['"Pablo"', '"Rodriguez"', '"email2+alias@test.com"', '"def"']
