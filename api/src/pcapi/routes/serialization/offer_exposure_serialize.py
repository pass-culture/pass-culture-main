import datetime
import typing

from pcapi.connectors.clickhouse.queries.offer_cumulative_view import OfferCumulativeViewCounts
from pcapi.core.highlights import models as highlights_models
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.constants import MAX_EXPOSURE_EVENTS
from pcapi.core.offers.constants import ExposureEventType
from pcapi.routes.serialization import HttpBodyModel
from pcapi.utils import date as date_utils


class ExposureEventResponseModel(HttpBodyModel):
    type: ExposureEventType
    name: str | None
    start_date: datetime.datetime
    end_date: datetime.datetime | None
    views_on_period: int | None

    # Headline timespans are stored as naive-UTC datetimes
    @classmethod
    def build_headline(cls, headline: offers_models.HeadlineOffer) -> typing.Self:
        return cls(
            type=ExposureEventType.HEADLINE,
            name=None,
            start_date=headline.timespan.lower,
            end_date=headline.timespan.upper,
            views_on_period=None,
        )

    # Highlight dates are stored as bare calendar dates, we read them as local datetimes then convert to naive UTC
    @classmethod
    def build_highlight(cls, highlight: highlights_models.Highlight, timezone: str) -> typing.Self:
        datespan = highlight.highlight_datespan
        start_date = date_utils.local_date_to_naive_utc_datetime(
            highlight.communication_date, datetime.time.min, timezone
        )
        # DATERANGE upper bound is exclusive: subtract one day for inclusive display
        inclusive_end_date = (
            date_utils.local_date_to_naive_utc_datetime(
                datespan.upper - datetime.timedelta(days=1), datetime.time.max, timezone
            )
            if datespan.upper
            else None
        )
        return cls(
            type=ExposureEventType.HIGHLIGHT,
            name=highlight.name,
            start_date=start_date,
            end_date=inclusive_end_date,
            views_on_period=None,
        )

    # ProAdvice.updatedAt is stored as a naive-UTC datetime
    @classmethod
    def build_pro_advice(cls, pro_advice: offers_models.ProAdvice) -> typing.Self:
        return cls(
            type=ExposureEventType.PRO_ADVICE,
            name=None,
            start_date=pro_advice.updatedAt,
            # Pro advice never ends
            end_date=None,
            views_on_period=None,
        )


class GetOfferExposureResponseModel(HttpBodyModel):
    views: int | None
    events: list[ExposureEventResponseModel]

    @classmethod
    def build(cls, offer: offers_models.Offer, cumulative_views: OfferCumulativeViewCounts) -> typing.Self:
        now = date_utils.get_naive_utc_now()

        # Highlights run on each offer's local calendar day, so they are evaluated in the
        # offer's own timezone (venue's address as a fallback).
        offerer_address = offer.offererAddress or offer.venue.offererAddress
        timezone = offerer_address.address.timezone

        events = [ExposureEventResponseModel.build_headline(headline) for headline in offer.headlineOffers]
        events += [
            ExposureEventResponseModel.build_highlight(criterion.highlight, timezone)
            for criterion in offer.criteria
            if criterion.highlightId
        ]
        if offer.proAdvice:
            events.append(ExposureEventResponseModel.build_pro_advice(offer.proAdvice))

        # Only expose events that have already started, most recent first
        started_events = [event for event in events if event.start_date <= now]
        started_events.sort(key=lambda event: event.start_date, reverse=True)
        events = started_events[:MAX_EXPOSURE_EVENTS]

        for event in events:
            event.views_on_period = cumulative_views.count_on_period(event.start_date, event.end_date or now)

        return cls(views=cumulative_views.count_at(now), events=events)
