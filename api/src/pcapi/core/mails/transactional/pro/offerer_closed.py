import datetime
from functools import partial

from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import repository as users_repository
from pcapi.repository import on_commit
from pcapi.utils.date import get_date_formatted_for_email


def get_offerer_closed_email_data(
    offerer: offerers_models.Offerer, closure_date: datetime.date | None
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.OFFERER_CLOSED.value,
        params={
            "OFFERER_NAME": offerer.name,
            "SIREN": offerer.siren,
            "END_DATE": get_date_formatted_for_email(closure_date) if closure_date else "",
            "HAS_THING_BOOKINGS": False,
            "HAS_EVENT_BOOKINGS": False,
        },
    )


def send_offerer_closed_email_to_pro(offerer: offerers_models.Offerer, closure_date: datetime.date | None) -> None:
    pro_users = users_repository.get_users_with_validated_attachment(offerer)
    data = get_offerer_closed_email_data(offerer, closure_date)
    for pro_user in pro_users:
        on_commit(partial(mails.send, recipients=[pro_user.email], data=data))
