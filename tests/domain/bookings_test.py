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
            stock = create_stock(offer=offer, price=10)
            booking = create_booking(token=1, stock=stock, user=user)

            # when
            generate_qr_code(booking)

            # then
            build_qr_code.assert_called_once_with(
                version=20,
                error_correction=3,
                box_size=2,
                border=1,
            )

        @patch('domain.bookings.qrcode.QRCode.add_data')
        def test_should_build_qr_code_with_the_booking_information_when_offer_is_an_event(
                self,
                build_qr_code_booking_info
        ):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer, name='Zenith de Paris')
            product = create_product_with_event_type(event_name='Concert de Nekfeu')
            offer = create_offer_with_event_product(idx=1, product=product, venue=venue)
            stock = create_stock(available=10, offer=offer, price=10)
            booking = create_booking(quantity=1, token='ABCDE', stock=stock, user=user)

            # when
            generate_qr_code(booking)

            # then
            build_qr_code_booking_info.assert_called_once_with(
                f'PASSCULTURE:v1;'
                f'TOKEN:ABCDE;'
                f'EMAIL:user@test.com;'
                f'OFFERID:AE;'
                f'OFFERNAME:Concert de Nekfeu;'
                f'VENUE:Zenith de Paris;'
                f'TYPE:EVENEMENT;'
                f'PRICE:10;'
                f'QUANTITY:1;'
            )

        @patch('domain.bookings.qrcode.QRCode.add_data')
        def test_should_build_qr_code_with_the_booking_information_when_offer_is_a_thing(
                self,
                build_qr_code_booking_info
        ):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer, name='Librairie du marais')
            product = create_product_with_thing_type(thing_name='One punch man')
            offer = create_offer_with_thing_product(idx=1, product=product, venue=venue)
            stock = create_stock(available=10, offer=offer, price=10)
            booking = create_booking(quantity=1, token='ABCDE', stock=stock, user=user)

            # when
            generate_qr_code(booking)

            # then
            build_qr_code_booking_info.assert_called_once_with(
                f'PASSCULTURE:v1;'
                f'TOKEN:ABCDE;'
                f'EMAIL:user@test.com;'
                f'OFFERID:AE;'
                f'OFFERNAME:One punch man;'
                f'VENUE:Librairie du marais;'
                f'TYPE:BIEN;'
                f'PRICE:10;'
                f'QUANTITY:1;'
            )

        @patch('domain.bookings.qrcode.QRCode.add_data')
        def test_should_build_qr_code_with_the_booking_information_when_offer_is_an_event_type_cinema(
                self,
                build_qr_code_booking_info
        ):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer, name='UGC Bercy')
            product = create_product_with_event_type(event_name='Avengers Endgame', event_type=EventType.CINEMA)
            offer = create_offer_with_thing_product(idx=1, product=product, venue=venue)
            stock = create_stock(available=10, beginning_datetime=datetime(2019, 1, 1, 12, 0, 0), offer=offer, price=10)
            booking = create_booking(quantity=1, token='ABCDE', stock=stock, user=user)

            # when
            generate_qr_code(booking)

            # then
            build_qr_code_booking_info.assert_called_with(
                f'PASSCULTURE:v1;'
                f'TOKEN:ABCDE;'
                f'EMAIL:user@test.com;'
                f'OFFERID:AE;'
                f'OFFERNAME:Avengers Endgame;'
                f'VENUE:UGC Bercy;'
                f'TYPE:EVENEMENT;'
                f'PRICE:10;'
                f'QUANTITY:1;'
                f'FORMULA:PLACE;'
                f'DATETIME:2019-01-01 12:00:00;'
            )

        @patch('domain.bookings.qrcode.QRCode.add_data')
        def test_should_build_qr_code_with_the_booking_information_when_offer_is_a_thing_type_cinema_abo(
                self,
                build_qr_code_booking_info
        ):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer, name='UGC Montparnasse')
            product = create_product_with_event_type(event_name='Terminator', event_type=ThingType.CINEMA_ABO)
            offer = create_offer_with_thing_product(idx=1, product=product, venue=venue)
            stock = create_stock(available=10, offer=offer, price=10)
            booking = create_booking(quantity=1, token='ABCDE', stock=stock, user=user)

            # when
            generate_qr_code(booking)

            # then
            build_qr_code_booking_info.assert_called_once_with(
                f'PASSCULTURE:v1;'
                f'TOKEN:ABCDE;'
                f'EMAIL:user@test.com;'
                f'OFFERID:AE;'
                f'OFFERNAME:Terminator;'
                f'VENUE:UGC Montparnasse;'
                f'TYPE:BIEN;'
                f'PRICE:10;'
                f'QUANTITY:1;'
                f'FORMULA:ABO;'
            )

        @patch('domain.bookings.qrcode.QRCode.add_data')
        def test_should_build_qr_code_with_the_booking_information_when_offer_is_an_event_with_a_beginning_date_time(
                self,
                build_qr_code_booking_info
        ):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer, name='UGC Châtelet')
            product = create_product_with_event_type(event_name='Spider-man Homecoming', event_type=ThingType.CINEMA_ABO)
            offer = create_offer_with_thing_product(idx=1, product=product, venue=venue)
            stock = create_stock(available=10, beginning_datetime=datetime(2019, 7, 20, 12, 0, 0), offer=offer, price=10)
            booking = create_booking(quantity=1, token='ABCDE', stock=stock, user=user)

            # when
            generate_qr_code(booking)

            # then
            build_qr_code_booking_info.assert_called_once_with(
                f'PASSCULTURE:v1;'
                f'TOKEN:ABCDE;'
                f'EMAIL:user@test.com;'
                f'OFFERID:AE;'
                f'OFFERNAME:Spider-man Homecoming;'
                f'VENUE:UGC Châtelet;'
                f'TYPE:BIEN;'
                f'PRICE:10;'
                f'QUANTITY:1;'
                f'FORMULA:ABO;'
                f'DATETIME:2019-07-20 12:00:00;'
            )


        @patch('domain.bookings.qrcode.QRCode.add_data')
        def test_should_build_qr_code_with_the_booking_information_including_isbn_when_offer_is_a_thing(
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
            booking = create_booking(token='ABCDE', stock=stock, user=user)

            # when
            generate_qr_code(booking)

            # then
            build_qr_code_booking_info.assert_called_once_with(
                f'PASSCULTURE:v1;'
                f'TOKEN:ABCDE;'
                f'EMAIL:user@test.com;'
                f'OFFERID:AE;'
                f'OFFERNAME:Naruto;'
                f'VENUE:Librairie de Belleville;'
                f'TYPE:BIEN;'
                f'PRICE:10;'
                f'QUANTITY:1;'
                f'EAN13:123456789;'
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
            venue = create_venue(offerer, name='UGC La Défense')
            product = create_product_with_event_type(event_type=ThingType.CINEMA_ABO)
            offer = create_offer_with_thing_product(idx=1, product=product, venue=venue)
            stock = create_stock(available=10, beginning_datetime=datetime(2019, 7, 20, 12, 0, 0), offer=offer)
            booking = create_booking(quantity=1, token='ABCDE', stock=stock, user=user)

            # when
            qr_code = generate_qr_code(booking)

            # then
            assert type(qr_code) is str
            assert qr_code == "data:image/png;base64,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"
