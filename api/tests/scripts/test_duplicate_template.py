from collections import namedtuple
from contextlib import suppress
import csv
from datetime import datetime
import io
import sys
import typing

import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.models import db


OfferAndStock = namedtuple("OfferAndStock", ["offer", "stock"])
OffersAndStocks = typing.Sequence[OfferAndStock]

OFFER_FIELDS = set(vars(models.CollectiveOffer).keys())
TEMPLATE_FIELDS = set(vars(models.CollectiveOfferTemplate).keys())
COMMON_FIELDS = OFFER_FIELDS & TEMPLATE_FIELDS


class OfferNotFoundError(Exception):
    pass


def load_rows(path: str | io.StringIO) -> typing.Sequence[dict]:
    if isinstance(path, io.StringIO):
        return list(csv.DictReader(path))

    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_ids(path: str | io.StringIO, rows: OffersAndStocks) -> None:
    fieldnames = ["offer_id", "stock_id"]

    if isinstance(path, io.StringIO):
        path.write("offer_id,stock_id\n")
        for row in rows:
            path.write(f"{row.offer.id},{row.stock.id}\n")
    else:
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            for row in rows:
                writer.writerow({"offer_id": row.offer.id, "stock_id": row.stock.id})


def fetch_template_offer(offer_id: int) -> models.CollectiveOfferTemplate:
    offer = models.CollectiveOfferTemplate.query.get(offer_id)
    if not offer:
        raise OfferNotFoundError()
    return offer


def format_students(data: dict) -> list[models.StudentLevels]:
    return [models.StudentLevels[data["Niveau de la classe"]]]


def format_beginning(data: dict) -> datetime:
    day = data["Date de l'intervention"].strip()
    time_of_the_day = data["Horaire"].strip()
    return datetime.strptime(f"{day} {time_of_the_day}", "%d/%m/%Y %H:%M")


def format_price(data: dict) -> float:
    return float(data["Prix global"])


def format_number_of_tickets(data: dict) -> int:
    return int(data["Nombre de places"])


def format_limit_booking_date(data: dict) -> datetime:
    return datetime.strptime(data["Date limite de résa"].strip(), "%d/%m/%Y")


def format_institution(data: dict) -> int:
    return int(data["Institution ID"].strip())


def duplicate_one_row(template: models.CollectiveOfferTemplate, data: dict) -> OfferAndStock:
    # offers and templates do not have the same fields
    template_data = {k: v for k, v in vars(template).items() if k in COMMON_FIELDS}

    with suppress(KeyError):
        del template_data["_sa_instance_state"]

    with suppress(KeyError):
        del template_data["id"]

    update_data = {
        **template_data,
        "isActive": True,
        "students": format_students(data),
        "institutionId": format_institution(data),
        "offerVenue": {"addresType": "school", "venueId": None, "otherAddress": ""},
    }

    offer = models.CollectiveOffer(**update_data)
    stock = models.CollectiveStock(
        collectiveOffer=offer,
        beginningDatetime=format_beginning(data),
        price=format_price(data),
        numberOfTickets=format_number_of_tickets(data),
        bookingLimitDatetime=format_limit_booking_date(data),
    )

    db.session.add(offer)
    db.session.add(stock)

    return OfferAndStock(offer=offer, stock=stock)


def duplicate_and_adapt_offer(path: str | io.StringIO, template_id: int) -> OffersAndStocks:
    rows = load_rows(path)
    template = fetch_template_offer(template_id)

    try:
        offers_stocks = [duplicate_one_row(template, row) for row in rows]
    except Exception as err:  # pylint: disable=broad-exception-caught
        db.session.rollback()
        sys.exit(f"Error: failed to duplicate offer: {err}")

    try:
        template.isActive = False
        db.session.add(template)
    except Exception as err:  # pylint: disable=broad-exception-caught
        db.session.rollback()
        sys.exit(f"Error: failed to add to disable template: {err}")

    try:
        db.session.commit()
    except Exception as err:  # pylint: disable=broad-exception-caught
        db.session.rollback()
        sys.exit(f"Error: failed to commit changes: {err}")
    else:
        return offers_stocks


@pytest.mark.usefixtures("db_session")
def test_duplicate_template() -> None:
    template = factories.CollectiveOfferTemplateFactory(isActive=True)

    institution = factories.EducationalInstitutionFactory()
    other_institution = factories.EducationalInstitutionFactory()

    start = datetime(2123, 10, 15, 10)
    limit_date = datetime(2123, 12, 15)

    ticket_count_1 = 20
    ticket_count_2 = 25
    total_price = 100

    duplicate_info = [
        (
            "Institution ID,Code UAI,Type d'étab.,Nom établissement,"
            "Code postal,COMMUNE,Niveau de la classe,Date de l'intervention,"
            "Horaire,Nombre de places,Prix global,Date limite de résa\n"
        ),
        (
            f"{institution.id},{institution.institutionId},"
            "{institution.institutionType},{institution.name},{institution.postalCode},"
            f"Commune-sur-quelquepart,GENERAL1,{start.strftime('%d/%m/%Y')},"
            f"{start.strftime('%H:%M')},{ticket_count_1},{total_price},"
            f"{limit_date.strftime('%d/%m/%Y')}\n"
        ),
        (
            f"{other_institution.id},{other_institution.institutionId},"
            "{other_institution.institutionType},{other_institution.name},{other_institution.postalCode},"
            f"Autre-Commune-sur-quelquepart,GENERAL2,{start.strftime('%d/%m/%Y')},"
            f"{start.strftime('%H:%M')},{ticket_count_2},{total_price},"
            f"{limit_date.strftime('%d/%m/%Y')}\n"
        ),
    ]

    fake_path = io.StringIO()
    for row in duplicate_info:
        fake_path.write(row)
    fake_path.seek(0)  # rewind

    offers_and_stocks = duplicate_and_adapt_offer(fake_path, template.id)
    db.session.refresh(template)

    assert not template.isActive
    assert len(offers_and_stocks) == 2

    offers_and_stocks = sorted(offers_and_stocks, key=lambda row: row.offer.id)

    assert offers_and_stocks[0].stock.price == total_price
    assert offers_and_stocks[0].stock.numberOfTickets == ticket_count_1
    assert offers_and_stocks[0].stock.beginningDatetime == start
    assert offers_and_stocks[0].stock.bookingLimitDatetime == limit_date
    assert offers_and_stocks[0].offer.institutionId == institution.id

    assert offers_and_stocks[1].stock.price == total_price
    assert offers_and_stocks[1].stock.numberOfTickets == ticket_count_2
    assert offers_and_stocks[1].stock.beginningDatetime == start
    assert offers_and_stocks[1].stock.bookingLimitDatetime == limit_date
    assert offers_and_stocks[1].offer.institutionId == other_institution.id

    out_buff = io.StringIO()
    save_ids(out_buff, offers_and_stocks)
    out_buff.seek(0)

    assert out_buff.read() == (
        "offer_id,stock_id\n"
        f"{offers_and_stocks[0].offer.id},{offers_and_stocks[0].stock.id}\n"
        f"{offers_and_stocks[1].offer.id},{offers_and_stocks[1].stock.id}\n"
    )
