from datetime import datetime
from unittest.mock import patch

import qrcode
import qrcode.image.svg

from domain.bookings import generate_qr_code
from models import EventType, ThingType
from tests.test_utils import create_booking, create_user, create_offer_with_event_product, create_venue, \
    create_product_with_event_type, create_stock, create_offerer, create_offer_with_thing_product, \
    create_product_with_thing_type


class BookingsTest:
    class GenerateBookingCodeTest:
        @patch('domain.bookings.qrcode.QRCode')
        def test_should_build_qr_code_with_the_correct_technical_parameters(self,
                                                                            build_qr_code):
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
                version=20,
                error_correction=3,
                box_size=10,
                border=4,
            )

        @patch('domain.bookings.qrcode.QRCode.add_data')
        def test_should_build_qr_code_with_the_booking_information_when_offer_is_an_event(self,
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
                f'PASSCULTURE:20;'
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
        def test_should_build_qr_code_with_the_booking_information_when_offer_is_a_thing(self,
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
                f'PASSCULTURE:20;'
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
                f'PASSCULTURE:20;'
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
                f'PASSCULTURE:20;'
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
                f'PASSCULTURE:20;'
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
                image_factory=qrcode.image.svg.SvgImage
            )
