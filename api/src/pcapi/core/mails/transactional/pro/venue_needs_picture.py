from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import models as offerer_models
from pcapi.utils import urls


def get_permanent_venue_needs_picture_data(venue: offerer_models.Venue) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.VENUE_NEEDS_PICTURE.value,
        params={
            "VENUE_NAME": venue.common_name,
            "VENUE_FORM_URL": urls.build_pc_pro_venue_link(venue),
        },
    )


def send_permanent_venue_needs_picture(venue: offerer_models.Venue) -> None:
    data = get_permanent_venue_needs_picture_data(venue)
    if not venue.bookingEmail:
        return
    mails.send(recipients=[venue.bookingEmail], data=data)
