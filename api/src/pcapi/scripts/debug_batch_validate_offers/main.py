import datetime
import os
from functools import partial
from typing import Iterable

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

import pcapi.core.mails.transactional as transactional_mails
from pcapi.app import app
from pcapi.core.mails.models import TransactionalEmailData
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import on_commit


OFFER_IDS = [
    323806585,
    323806915,
    323808073,
    323808130,
    323810285,
    323831196,
    323836552,
    323836553,
    323836558,
    323836560,
    323836561,
    323836562,
    323836564,
    323836565,
    323836566,
    323836567,
    323862590,
    323864037,
    323864214,
    323864664,
    323868581,
]


@atomic()
def run() -> None:
    with open(f"{os.environ.get('OUTPUT_DIRECTORY')}/run.txt", "w") as f:
        max_price_subquery = (
            sa.select(sa.func.max(offers_models.Stock.price))
            .select_from(offers_models.Stock)
            .filter(
                offers_models.Stock.offerId == offers_models.Offer.id,
                sa.not_(offers_models.Stock.isSoftDeleted),
            )
            .correlate(offers_models.Offer)
            .scalar_subquery()
        )
        query = (
            db.session.query(
                offers_models.Offer,
                max_price_subquery.label("max_price"),
            )
            .outerjoin(offers_models.Offer.futureOffer)
            .filter(offers_models.Offer.id.in_(OFFER_IDS))
            .options(
                sa_orm.joinedload(offers_models.Offer.venue).load_only(
                    offerers_models.Venue.bookingEmail, offerers_models.Venue.name, offerers_models.Venue.publicName
                ),
                sa_orm.joinedload(offers_models.Offer.offererAddress).options(
                    sa_orm.joinedload(offerers_models.OffererAddress.address),
                    sa_orm.selectinload(offerers_models.OffererAddress.venues),
                ),
            )
            .options(sa_orm.contains_eager(offers_models.Offer.futureOffer))
        )
        f.write(f"{query}\n")
        f.write("-----")
        offers = query.all()

        for offer, max_price in offers:
            recipients = (
                [offer.venue.bookingEmail]
                if offer.venue.bookingEmail
                else [recipient.user.email for recipient in offer.venue.managingOfferer.UserOfferers]
            )

            offer_data = transactional_mails.get_email_data_from_offer(
                offer, OfferValidationStatus.PENDING, OfferValidationStatus.APPROVED
            )
            assert offer_data  # helps mypy

            f.write(f"{datetime.datetime.utcnow().isoformat()}\n")
            f.write(f"{offer}\n")
            f.write(f"offer.venue: {offer.venue}\n")
            f.write(f"offer.venue.bookingEmail: {offer.venue.bookingEmail}\n")
            f.write(f"template: {offer_data.template}\n")
            f.write(f"params: {offer_data.params}\n")
            f.write(f"offer.offererAddress: {offer.offererAddress}\n")
            f.write(f"offer.offererAddress.address: {offer.offererAddress.address}\n")
            f.write(f"offer.offererAddress.venues: {offer.offererAddress.venues}\n")
            f.write("-----\n")

            on_commit(
                partial(
                    send_mail,
                    recipients=recipients,
                    bcc_recipients=[],
                    data=offer_data,
                )
            )

    db.session.flush()


def send_mail(
    recipients: Iterable,
    data: TransactionalEmailData,
    bcc_recipients: Iterable[str] = (),
) -> None:
    with open(f"{os.environ.get('OUTPUT_DIRECTORY')}/send_mail.txt", "a") as f:
        f.write(f"{datetime.datetime.utcnow().isoformat()}\n")
        f.write(f"recipients: {recipients}\n")
        f.write(f"data: {data}\n")
        f.write(f"bcc_recipients: {bcc_recipients}\n")
        f.write("-----\n")


if __name__ == "__main__":
    app.app_context().push()
    run()
