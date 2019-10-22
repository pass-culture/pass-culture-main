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
                version=20,
                error_correction=3,
                box_size=1,
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
            )

        def test_should_build_qr_code_image_as_bytes(self):
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
            assert qr_code == "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGMAAABjAQAAAACnQIM4AAAFcUlEQVR4nFXU+TvUeQDA8c/n6zuYpKgoNmac48yx2lY5RsiVq1p0rHvDZMNurdqn2tltc5TSU1k25EhuzzYiHYbBGDHROtOYzHcwIwozjpgxY/a33Wff/8DrtzdUgP/iAyo7J8WU2BgqvaFFJMIWvEg6e7grQGnMJ0uMTA1tzTcya2ZtybpyEcDSQNqnkTXinf2cb83XENBVE6uHM6BwroQBgOweqwFNyiZXU0J7ugCkWvwLfKZCxdJJJEG7NriPax/Gh5zJHOzvKLKnEa8IHwAnVUNsJU0FGQnvjvCF4HWsSkCZbqEKsA5pxdBBgiOQLfWuhRsY5/agglTudsVdo8mexPabdFTv8+S9S0v0hRtvPF8xQHGGsrVxvnxzs22QKwYWTnv6a61cFH/xXY1yJNq5tLPlRqJi5Xuv1moR+HOr50++8Ip33R+j7kSQVgx/stDlqbfZhi1Hgsk6j5PCJydkstNVfRhM28JQUopDCCuijiAW4nd33gfbNRtRw/ZlAciqz5jeEQUrjUJ5WDR4M+/WhbYel9lgD7cRYUOZVH2xIEZ3vxCRjCEmuWvBP3M3CHU5hzkMwBKrrlscU3S/E0UwI0GFjdvb5SaKSCYo4WJwSnwJwSXYL4nne/xYkNYwFZPUjjFh0OYBERBeNFmYCfPHqcpOWBcj+CVVrl+EcepeE5IpFSn5y+Je7551q1GKiy0ZPaPv//zE1IbR2R1GkkJwn7a0bh7ERq5/edA8Eq7TZJZxwaH9m0j9yiYonUIwPPTDyFw0jbMsAHLL3qzbgkzk6gBniIi2bZtI+nid761clX+GDIqEsYOUu53PZaa/kjBUktw67Ryu1LQrOWmCAeQfHWtPzZVu6QgyHSXCFsXTZEW4ikJJpOk+CIpizRSmFRyay6PzJAzmbfAm7I7r187aZe5whvI9hvtGz3/QWtHocvFG27ZPUMMpeJq7SG+JDIpWjLtNcYI2JyYkYTBvPOLyV4mfXq4T64AzlK/DcrqWpswjSqneG2ljvphMY8nNMljLjWRQlCoLNq2YT3F1uEbCEIlecGr01oEXIQNSJwaQ4+X0U/b1t9qPVo8SQXNi/vEJ3GVW4PMjNyNB4WpWiWmnsM3V4xoJQ+BlcVR00qRuZH21EwPKm5mlzjnM7oOTO/W9UXqH63Ca8qsqNlFiSQZFq7vdtNOnfnR1yCFhqERPZ5USiDUuz3K4DDRGbEz2s1eJkfaxG+Phi8XC2/1seVCHQ4LKPoSvpqyaTW5w1Ko5v40K8hxc2uFQ5gfiyG6lYrhwKyUYL3n2ixtHSKGjJW/VB8VMT1DowZmTInqEJwKeQRzen00rB3DR121VW/Pccm+Iua8X8siAMYdZmuU1Wo91AdS998A3Dp9ZmPFrrQ4qHEvMqMORmhfRp+kX+tHelYiu5cWSt0yuSRYDCcQxaggzjy/0Gzi/AmiJzVytgvsyyfL1fiMypJcf4NUBZ5FaX1n8FFw0dJy5PfSERT+UYLEKs8eLh3wKFwTCcfYIBgbOxm/uxpzE+Ll2k0jQ7c7b6LR4FB2inZuNofyJwPS1x4G4dh0SnwymI1iGWWjVg5JjM1aR4Hev/lvs0jft/h+QoxhiaWBox0sXPLupN0wAoJJEOPcbpwBd23SZT0QEQfL5B4nSTFxwbTUZbvg7emviSr1CGmgljrDuqYZas1hi9447PK2LDkvLC5TCtlvJCPn491BRnLrpvm+0nn4FphEPqTFlqjrr/NMP4+6Y7EVc+PM2GteSo9R1/LMBOsWvBGo0s+X3dtU+DAR4rM01JkrLO81rBwAKvr5wUH8l2qohLVeDAVv4vD6NccoDi8quNiagDmvUjQ1b6VQcuBRAhP976z8ei5Ba7vqYPQAAAABJRU5ErkJggg=="
