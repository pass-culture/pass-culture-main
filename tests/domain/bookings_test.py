from datetime import datetime
from unittest.mock import patch

from domain.bookings import generate_qr_code
from models import ThingType
from tests.model_creators.generic_creators import create_booking, create_user, create_stock, create_offerer, create_venue
from tests.model_creators.specific_creators import create_product_with_thing_type, create_product_with_event_type, \
    create_offer_with_thing_product, create_offer_with_event_product


class BookingsTest:
    class GenerateQrCodeTest:
        @patch('domain.bookings.qrcode.QRCode')
        def test_should_build_qr_code_with_the_correct_technical_parameters(
                self,
                build_qr_code
        ):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            product = create_product_with_event_type()
            offer = create_offer_with_event_product(product=product, venue=venue)
            stock = create_stock(offer=offer, price=10)
            booking = create_booking(user=user, stock=stock, token=1)

            # when
            generate_qr_code(booking)

            # then
            build_qr_code.assert_called_once_with(
                version=2,
                error_correction=3,
                box_size=5,
                border=1,
            )

        @patch('domain.bookings.qrcode.QRCode.add_data')
        def test_should_build_qr_code_with_booking_token_and_product_isbn_when_isbn_is_provided(
                self,
                build_qr_code_booking_info
        ):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer, name='Librairie de Belleville')
            product = create_product_with_thing_type(extra_data={'isbn': '123456789'}, thing_name='Naruto')
            offer = create_offer_with_thing_product(idx=1, product=product, venue=venue)
            stock = create_stock(available=10, offer=offer, price=10)
            booking = create_booking(user=user, stock=stock, token='ABCDE')

            # when
            generate_qr_code(booking)

            # then
            build_qr_code_booking_info.assert_called_once_with(
                f'PASSCULTURE:v2;'
                f'EAN13:123456789;'
                f'TOKEN:ABCDE'
            )

        @patch('domain.bookings.qrcode.QRCode.add_data')
        def test_should_build_qr_code_with_booking_token_and_no_product_isbn_when_isbn_is_not_provided(
                self,
                build_qr_code_booking_info
        ):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer, name='Librairie de Belleville')
            product = create_product_with_thing_type(extra_data=None, thing_name='Naruto')
            offer = create_offer_with_thing_product(idx=1, product=product, venue=venue)
            stock = create_stock(available=10, offer=offer, price=10)
            booking = create_booking(user=user, stock=stock, token='ABCDE')

            # when
            generate_qr_code(booking)

            # then
            build_qr_code_booking_info.assert_called_once_with(
                f'PASSCULTURE:v2;'
                f'TOKEN:ABCDE'
            )

        @patch('domain.bookings.qrcode.QRCode.make_image')
        def test_should_build_qr_code_with_correct_image_parameters(
                self,
                build_qr_code_image_parameters
        ):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            product = create_product_with_event_type(event_type=ThingType.CINEMA_ABO)
            offer = create_offer_with_thing_product(idx=1, product=product, venue=venue)
            stock = create_stock(beginning_datetime=datetime(2019, 7, 20, 12, 0, 0), offer=offer)
            booking = create_booking(user=user, stock=stock, token='ABCDE')

            # when
            generate_qr_code(booking)

            # then
            build_qr_code_image_parameters.assert_called_once_with(
                back_color='white',
                fill_color='black',
            )

        def test_should_build_qr_code_image_as_base64_string(self):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer, name='UGC La Défense')
            product = create_product_with_event_type(event_type=ThingType.CINEMA_ABO)
            offer = create_offer_with_thing_product(idx=1, product=product, venue=venue)
            stock = create_stock(available=10, beginning_datetime=datetime(2019, 7, 20, 12, 0, 0), offer=offer)
            booking = create_booking(user=user, quantity=1, stock=stock, token='ABCDE')

            # when
            qr_code = generate_qr_code(booking)

            # then
            assert type(qr_code) is str
            assert qr_code == "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJsAAACbAQAAAABdGtQhAAABs0lEQVR4nL1XMY7bMBCcFQXQqagf0EDeYSlp8o/8w7Hko/8VyfcR6gdURwKSJ4VdxYc0580WJDDFDHZJzoBCPNVcPWPAZ8EiIlKq5ZcUkWEWkfrTnB+DHRnRukDHBJAclIQoNeyI8758wwVFmhdwflD1fWMF2HNjXsL5b9BEdBw0hYQrIAkoXXOEZdIRQgaA3LoQc+tCBGCiihBJkiMMLVNPklQSmsiIjqvPrVs9mbQ6mpLhY2GI6BiUhG5uBW8uRDu6QMDpjK4uP3DxkLR9LSds+/wlKV1v+wYz4brYyGnmBGp5Xfk+r750zXEulav9ruOq5QxOxI6uhh2x7e3bSzifqwaW1QscPNikvuzQ/9Tp6ODDxBu2fekTAKFWHgFbhytMtL+bC3ZYdM4IWRJgR0daJkN7czoPtsLBD76cgDnTD8jvSS0m5nUGFtlLhU3ktOhE+d29c5d6kskwt0qje+SRcPBoXYhZy+uQOzJydCFaJsMsWnmUW5jIKT16g9boHuChMbyn31XpHT3AK46wZwlx176M829QuKL0Cdi1rp7t6HQs6H4yvOGIDPR6t07+12/iD1lz9hCJWM0gAAAAAElFTkSuQmCC"
