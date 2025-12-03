import datetime

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core.criteria import models as criterion_models
from pcapi.core.highlights import models as highlights_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db


def get_available_highlights() -> list[highlights_models.Highlight]:
    today = datetime.date.today()
    highlight_list = (
        db.session.query(highlights_models.Highlight)
        .filter(highlights_models.Highlight.availability_datespan.contains(today))
        .all()
    )
    return highlight_list


def get_today_highlight_requests() -> list[highlights_models.HighlightRequest]:
    today = datetime.date.today()

    return (
        db.session.query(highlights_models.HighlightRequest)
        .join(highlights_models.HighlightRequest.highlight)
        .join(highlights_models.HighlightRequest.offer)
        .join(offers_models.Offer.venue)
        .join(highlights_models.Highlight.criteria)
        .join(
            criterion_models.OfferCriterion,
            sa.and_(
                criterion_models.OfferCriterion.offerId == offers_models.Offer.id,
                criterion_models.OfferCriterion.criterionId == criterion_models.Criterion.id,
            ),
        )
        .filter(highlights_models.Highlight.communication_date == today)
        .options(
            sa_orm.contains_eager(highlights_models.HighlightRequest.offer)
            .load_only(offers_models.Offer.name)
            .contains_eager(offers_models.Offer.venue)
            .load_only(offerers_models.Venue.bookingEmail)
        )
        .distinct(offerers_models.Venue.bookingEmail, highlights_models.Highlight.id)
    ).all()
