from datetime import datetime
from unittest.mock import patch

from domain.bookings import generate_qr_code
from models import EventType, ThingType
from tests.test_utils import create_booking, create_user, create_offer_with_event_product, create_venue, \
    create_product_with_event_type, create_stock, create_offerer, create_offer_with_thing_product, \
    create_product_with_thing_type


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
            stock = create_stock(offer=offer)
            booking = create_booking(token=1, stock=stock, user=user)

            # when
            generate_qr_code(booking)

            # then
            build_qr_code.assert_called_once_with(
                version=10,
                error_correction=3,
                box_size=10,
                border=4,
            )

        @patch('domain.bookings.qrcode.QRCode.add_data')
        def test_should_build_qr_code_with_the_booking_information_when_offer_is_an_event(
                self,
                build_qr_code_booking_info
        ):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            product = create_product_with_event_type()
            offer = create_offer_with_event_product(idx=1, product=product, venue=venue)
            stock = create_stock(offer=offer)
            booking = create_booking(token='ABCDE', stock=stock, user=user)

            # when
            generate_qr_code(booking)

            # then
            build_qr_code_booking_info.assert_called_once_with(
                f'PASSCULTURE:v1;'
                f'TOKEN:ABCDE;'
                f'EMAIL:user@test.com;'
                f'OFFERID:AE;'
                f'OFFERNAME:Test event;'
                f'VENUE:La petite librairie;'
                f'TYPE:EVT;'
                f'FORMULA:;'
                f'DATETIME:;'
                f'PRICE:10;'
                f'QTY:1'
            )

        @patch('domain.bookings.qrcode.QRCode.add_data')
        def test_should_build_qr_code_with_the_booking_information_when_offer_is_a_thing(
                self,
                build_qr_code_booking_info
        ):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            product = create_product_with_thing_type()
            offer = create_offer_with_thing_product(idx=1, product=product, venue=venue)
            stock = create_stock(offer=offer)
            booking = create_booking(token='ABCDE', stock=stock, user=user)

            # when
            generate_qr_code(booking)

            # then
            build_qr_code_booking_info.assert_called_once_with(
                f'PASSCULTURE:v1;'
                f'TOKEN:ABCDE;'
                f'EMAIL:user@test.com;'
                f'OFFERID:AE;'
                f'OFFERNAME:Test Book;'
                f'VENUE:La petite librairie;'
                f'TYPE:BIEN;'
                f'FORMULA:;'
                f'DATETIME:;'
                f'PRICE:10;'
                f'QTY:1'
            )

        @patch('domain.bookings.qrcode.QRCode.add_data')
        def test_should_build_qr_code_with_the_booking_information_when_offer_is_an_event_type_cinema(
                self,
                build_qr_code_booking_info
        ):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            product = create_product_with_event_type(event_type=EventType.CINEMA)
            offer = create_offer_with_thing_product(idx=1, product=product, venue=venue)
            stock = create_stock(offer=offer)
            booking = create_booking(token='ABCDE', stock=stock, user=user)

            # when
            generate_qr_code(booking)

            # then
            build_qr_code_booking_info.assert_called_once_with(
                f'PASSCULTURE:v1;'
                f'TOKEN:ABCDE;'
                f'EMAIL:user@test.com;'
                f'OFFERID:AE;'
                f'OFFERNAME:Test event;'
                f'VENUE:La petite librairie;'
                f'TYPE:EVT;'
                f'FORMULA:PLACE;'
                f'DATETIME:;'
                f'PRICE:10;'
                f'QTY:1'
            )

        @patch('domain.bookings.qrcode.QRCode.add_data')
        def test_should_build_qr_code_with_the_booking_information_when_offer_is_a_thing_type_cinema_abo(
                self,
                build_qr_code_booking_info
        ):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            product = create_product_with_event_type(event_type=ThingType.CINEMA_ABO)
            offer = create_offer_with_thing_product(idx=1, product=product, venue=venue)
            stock = create_stock(offer=offer)
            booking = create_booking(token='ABCDE', stock=stock, user=user)

            # when
            generate_qr_code(booking)

            # then
            build_qr_code_booking_info.assert_called_once_with(
                f'PASSCULTURE:v1;'
                f'TOKEN:ABCDE;'
                f'EMAIL:user@test.com;'
                f'OFFERID:AE;'
                f'OFFERNAME:Test event;'
                f'VENUE:La petite librairie;'
                f'TYPE:BIEN;'
                f'FORMULA:ABO;'
                f'DATETIME:;'
                f'PRICE:10;'
                f'QTY:1'
            )

        @patch('domain.bookings.qrcode.QRCode.add_data')
        def test_should_build_qr_code_with_the_booking_information_when_offer_is_an_event_with_a_beginning_date_time(
                self,
                build_qr_code_booking_info
        ):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            product = create_product_with_event_type(event_type=ThingType.CINEMA_ABO)
            offer = create_offer_with_thing_product(idx=1, product=product, venue=venue)
            stock = create_stock(beginning_datetime=datetime(2019, 7, 20, 12, 0, 0), offer=offer)
            booking = create_booking(token='ABCDE', stock=stock, user=user)

            # when
            generate_qr_code(booking)

            # then
            build_qr_code_booking_info.assert_called_once_with(
                f'PASSCULTURE:v1;'
                f'TOKEN:ABCDE;'
                f'EMAIL:user@test.com;'
                f'OFFERID:AE;'
                f'OFFERNAME:Test event;'
                f'VENUE:La petite librairie;'
                f'TYPE:BIEN;'
                f'FORMULA:ABO;'
                f'DATETIME:2019-07-20 12:00:00;'
                f'PRICE:10;'
                f'QTY:1'
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
            booking = create_booking(token='ABCDE', stock=stock, user=user)

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
            venue = create_venue(offerer)
            product = create_product_with_event_type(event_type=ThingType.CINEMA_ABO)
            offer = create_offer_with_thing_product(idx=1, product=product, venue=venue)
            stock = create_stock(beginning_datetime=datetime(2019, 7, 20, 12, 0, 0), offer=offer)
            booking = create_booking(token='ABCDE', stock=stock, user=user)

            # when
            qr_code = generate_qr_code(booking)

            # then
            assert type(qr_code) is str
            assert qr_code == "data:image/png;base64,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"
