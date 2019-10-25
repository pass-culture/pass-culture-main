import base64
import csv
import io
from datetime import timedelta
from io import StringIO
from typing import List, Iterator

import qrcode
import qrcode.image.svg
from PIL import Image

from models import Booking
from models.offer_type import EventType, ThingType
from models.stock import Stock
from utils.human_ids import humanize

BOOKING_CANCELLATION_DELAY = timedelta(hours=72)
QR_CODE_PASS_CULTURE_VERSION = 'v1'
QR_CODE_VERSION = 20
QR_CODE_BOX_SIZE = 2
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


def generate_bookings_details_csv(bookings: List[Booking]) -> str:
    output = StringIO()
    csv_lines = [booking.as_csv_row() for booking in bookings]
    writer = csv.writer(output, dialect=csv.excel, delimiter=";")
    writer.writerow(CSV_HEADER)
    writer.writerows(csv_lines)
    return output.getvalue()


def filter_bookings_to_compute_remaining_stock(stock: Stock) -> Iterator:
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

    offer_formula = ''
    if booking.stock.offer.type == str(EventType.CINEMA):
        offer_formula = 'PLACE'
    elif booking.stock.offer.type == str(ThingType.CINEMA_ABO):
        offer_formula = 'ABO'

    offer_type = 'EVENEMENT' if booking.stock.offer.isEvent else 'BIEN'
    offer_date_time = booking.stock.beginningDatetime if booking.stock.beginningDatetime else ''
    offer_extra_data = booking.stock.offer.extraData

    product_isbn = ''
    if offer_extra_data and 'isbn' in offer_extra_data:
        product_isbn = offer_extra_data['isbn']

    data = f'PASSCULTURE:{QR_CODE_PASS_CULTURE_VERSION};' \
           f'TOKEN:{booking.token};' \
           f'EMAIL:{booking.user.email};' \
           f'OFFERID:{humanize(booking.stock.offer.id)};' \
           f'OFFERNAME:{booking.stock.offer.name};' \
           f'VENUE:{booking.stock.offer.venue.name};' \
           f'TYPE:{offer_type};' \
           f'PRICE:{booking.stock.price};' \
           f'QUANTITY:{booking.quantity};'

    if offer_formula != '':
        data += f'FORMULA:{offer_formula};'

    if offer_date_time != '':
        data += f'DATETIME:{offer_date_time};'

    if product_isbn != '':
        data += f'EAN13:{product_isbn};'

    qr.add_data(data)
    image = qr.make_image(fill_color='black', back_color='white')
    return _convert_image_to_base64(image)


def _convert_image_to_base64(image: Image) -> str:
    image_as_bytes = io.BytesIO()
    image.save(image_as_bytes)
    image_as_base64 = base64.b64encode(image_as_bytes.getvalue())
    return f'data:image/png;base64,{str(image_as_base64, encoding="utf-8")}'
