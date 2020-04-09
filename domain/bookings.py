import base64
import csv
import io
from collections import namedtuple
from datetime import timedelta
from io import StringIO
from typing import List, Iterator

import qrcode
import qrcode.image.svg
from PIL import Image

from models.booking import Booking
from models.stock import StockSQLEntity
from utils.string_processing import format_decimal

BOOKING_CANCELLATION_DELAY = timedelta(hours=72)
QR_CODE_PASS_CULTURE_VERSION = 'v2'
QR_CODE_VERSION = 2
QR_CODE_BOX_SIZE = 5
QR_CODE_BOX_BORDER = 1
CSV_HEADER = [
    "Raison sociale du lieu",
    "Nom de l'offre",
    "Nom utilisateur",
    "Prénom utilisateur",
    "E-mail utilisateur",
    "Date de la réservation",
    "Quantité",
    "Tarif pass Culture",
    "Statut",
]


def generate_bookings_details_csv(bookings_info: List[namedtuple]) -> str:
    output = StringIO()

    csv_lines = _generate_csv_lines(bookings_info)

    writer = csv.writer(output, dialect=csv.excel, delimiter=";")
    writer.writerow(CSV_HEADER)
    writer.writerows(csv_lines)
    return output.getvalue()


def _generate_csv_lines(bookings_info: List[namedtuple]) -> List[List]:
    csv_lines = []
    for booking in bookings_info:
        status_label = _compute_booking_status_label(booking)

        booking_details = [
            booking.venue_name,
            booking.offer_name,
            booking.user_lastname,
            booking.user_firstname,
            booking.user_email,
            booking.date_created,
            format_decimal(booking.quantity),
            booking.amount,
            status_label
        ]
        csv_lines.append(booking_details)
    return csv_lines


def _compute_booking_status_label(booking_info: namedtuple) -> str:
    if booking_info.isCancelled:
        return "Réservation annulée"
    elif booking_info.isUsed:
        return "Contremarque validée"
    return "En attente"


def filter_bookings_to_compute_remaining_stock(stock: StockSQLEntity) -> Iterator:
    return filter(lambda b: not b.isCancelled
                            and not b.isUsed
                            or (b.isUsed
                                and b.dateUsed
                                and b.dateUsed >= stock.dateModified),
                  stock.bookings)


def generate_qr_code(booking: Booking) -> str:
    qr = qrcode.QRCode(
        version=QR_CODE_VERSION,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=QR_CODE_BOX_SIZE,
        border=QR_CODE_BOX_BORDER,
    )

    offer_extra_data = booking.stock.offer.extraData
    product_isbn = ''
    if offer_extra_data and 'isbn' in offer_extra_data:
        product_isbn = offer_extra_data['isbn']

    data = f'PASSCULTURE:{QR_CODE_PASS_CULTURE_VERSION};'

    if product_isbn != '':
        data += f'EAN13:{product_isbn};'

    data += f'TOKEN:{booking.token}'

    qr.add_data(data)
    image = qr.make_image(fill_color='black', back_color='white')
    return _convert_image_to_base64(image)


def _convert_image_to_base64(image: Image) -> str:
    image_as_bytes = io.BytesIO()
    image.save(image_as_bytes)
    image_as_base64 = base64.b64encode(image_as_bytes.getvalue())
    return f'data:image/png;base64,{str(image_as_base64, encoding="utf-8")}'
