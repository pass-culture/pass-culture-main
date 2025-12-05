import datetime

from pcapi.core.criteria import models as criterion_models
from pcapi.core.highlights import models as highlights_models
from pcapi.core.highlights.models import HighlightRequest
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


def get_today_highlight_requests() -> list[HighlightRequest]:
    today = datetime.date.today()
    return (
        db.session.query(highlights_models.HighlightRequest)
        .join(highlights_models.Highlight, highlights_models.HighlightRequest.highlight)
        .join(offers_models.Offer, highlights_models.HighlightRequest.offer)
        .join(offerers_models.Venue, offers_models.Offer.venue)
        .join(criterion_models.Criterion, highlights_models.Highlight.criteria)
        .join(criterion_models.OfferCriterion, criterion_models.OfferCriterion.offerId == offers_models.Offer.id)
        .filter(highlights_models.Highlight.communication_date == today)
        .distinct(offerers_models.Venue.bookingEmail, highlights_models.Highlight.id)
    ).all()
