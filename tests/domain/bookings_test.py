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
                f'PRICE:10;'
                f'QTY:1;'
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
                f'PRICE:10;'
                f'QTY:1;'
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
            stock = create_stock(beginning_datetime=datetime(2019, 1, 1, 12, 0, 0), offer=offer)
            booking = create_booking(token='ABCDE', stock=stock, user=user)

            # when
            generate_qr_code(booking)

            # then
            build_qr_code_booking_info.assert_called_with(
                f'PASSCULTURE:v1;'
                f'TOKEN:ABCDE;'
                f'EMAIL:user@test.com;'
                f'OFFERID:AE;'
                f'OFFERNAME:Test event;'
                f'VENUE:La petite librairie;'
                f'TYPE:EVT;'
                f'PRICE:10;'
                f'QTY:1;'
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
                f'PRICE:10;'
                f'QTY:1;'
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
                f'PRICE:10;'
                f'QTY:1;'
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
            venue = create_venue(offerer)
            product = create_product_with_thing_type(extra_data={'isbn': '123456789'})
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
                f'PRICE:10;'
                f'QTY:1;'
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
            venue = create_venue(offerer)
            product = create_product_with_event_type(event_type=ThingType.CINEMA_ABO)
            offer = create_offer_with_thing_product(idx=1, product=product, venue=venue)
            stock = create_stock(beginning_datetime=datetime(2019, 7, 20, 12, 0, 0), offer=offer)
            booking = create_booking(token='ABCDE', stock=stock, user=user)

            # when
            qr_code = generate_qr_code(booking)

            # then
            assert type(qr_code) is str
            assert qr_code == "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAH4AAAB+AQAAAADKWJglAAADCUlEQVR4nIVWsYpdRwyVn7Z5INBCKoNLQ6qFgXlgAhNmwW1+ImBwteAP8C8YAlsF8hOBQCqDzGwT0KKFrQIu3QZm0QU3ekzaJFeQ6S4cpCPpHOk+W/Cvdz7Af59AAFYjAVEjoB3iwLEp0bbxfPf1DSzZIS7OlxOefsXy9M3Hck+f9jGe6fXvV/TqA70FkPPnLckC8B1e/nS93Z/Pz1+8A9gztTAX7zwKrhlL91nkWv/xedpngbWsOg6z6TrWij1iRtRVAGgMBap7xAFe3cH1rbpf0Vv89viwj6FSYnAhYYPaR9IP/3xze94QbuxyixMck7k0ntbWpDAUkqSW6Y1JCau5Y7WkFm9sqnNy4KBZ9x2DuYqNKQPFwwTbnmlsCM+/PLw++j3Adp3xqLNFZWy4qteSZInJTQRVi+GckSCEYyyLYA/kOTMErRKkTWSpLEmqDZS2BNrC0btAgpDmdTlg1DBhTBQ0H4+v2gYkp+PjFzr9nFRbqNWmIqOJsu47BoPXXLV4qdVG7dlcSletQ6WsDo2SGJOLluWs3sLHyHQqJAIqqBYqiW9hmFDnYTZcqmX6GGoRPUiKBmiCOBSEh9MnHKzbY8XtMtsfZNFEwNSHYNZ1lsaI3Ud37zPrWGNvYjWoigQl07cx58TZnSY4e+Ioe8LjG6E7QPge6n3GA6VJ0dq49DV71rEW5malszBG5rlVEVQ8NNZArolfxhG+vt/+eP3bPW0/lMePSZYeUkbV0dnYeqZ1nbXYaCKLncYecej4+Aufj1DebRsJlCSGNFduq6DqaCVTUO0ObdUoY1TOEAar6PJwYC/pXFaHgOYQrS1rnjDdznbS7c94wNu7DY8JU/UKzA2q43BN9joEtLGWNofSATSZi9jqk5cxVjLJPCfNQViACYdA4n1YS212Na3VFluWBWL4rGQMHTXRx4Fju3mBH8fTS76/QtzfSlCaOGgB6QCBbEspTdfRSRxbXZlvlXRZE2laVVtyX8BCeZawij0mJ648PF28LEzw4/n44eKz/LW/Ys/+99/hb/88/fXJk8CnAAAAAElFTkSuQmCC"
