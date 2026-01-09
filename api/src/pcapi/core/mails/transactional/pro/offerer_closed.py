import datetime

from pcapi.core import mails
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.educational import repository as educational_repository
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.users import repository as users_repository
from pcapi.models import db
from pcapi.utils.date import get_date_formatted_for_email


def get_offerer_closed_email_data(
    offerer: offerers_models.Offerer, is_manual: bool, closure_date: datetime.date | None
) -> models.TransactionalEmailData:
    bookings_subcategory_ids = [
        entities[0]
        for entities in (
            db.session.query(bookings_models.Booking)
            .filter(
                bookings_models.Booking.offererId == offerer.id,
                bookings_models.Booking.status.in_(
                    [bookings_models.BookingStatus.CONFIRMED, bookings_models.BookingStatus.USED]
                ),
            )
            .join(bookings_models.Booking.stock)
            .join(offers_models.Stock.offer)
            .with_entities(offers_models.Offer.subcategoryId)
            .distinct()
        ).all()
    ]

    has_thing_bookings = False
    has_event_bookings = False

    for subcategory_id in bookings_subcategory_ids:
        subcategory = subcategories.ALL_SUBCATEGORIES_DICT.get(subcategory_id)
        if subcategory and subcategory.is_event:
            has_event_bookings = True
        else:
            has_thing_bookings = True

    if not has_event_bookings:
        has_event_bookings = educational_repository.offerer_has_ongoing_collective_bookings(
            offerer.id, include_used=True
        )

    template = TransactionalEmail.OFFERER_CLOSED_MANUALLY if is_manual else TransactionalEmail.OFFERER_CLOSED

    return models.TransactionalEmailData(
        template=template.value,
        params={
            "OFFERER_NAME": offerer.name,
            "SIREN": offerer.siren,
            "END_DATE": get_date_formatted_for_email(closure_date) if closure_date else "",
            "HAS_THING_BOOKINGS": has_thing_bookings,
            "HAS_EVENT_BOOKINGS": has_event_bookings,
        },
    )


def send_offerer_closed_email_to_pro(
    offerer: offerers_models.Offerer, is_manual: bool, closure_date: datetime.date | None
) -> None:
    pro_users = users_repository.get_users_with_validated_attachment(offerer)
    data = get_offerer_closed_email_data(offerer, is_manual, closure_date)
    for pro_user in pro_users:
        mails.send(recipients=[pro_user.email], data=data)
