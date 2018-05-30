""" HOQS: for High Order Queries :) like HOCS in React """
from datetime import datetime
from flask import current_app as app
from sqlalchemy import desc
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import func

Event = app.model.Event
EventOccurence = app.model.EventOccurence
Mediation = app.model.Mediation
Offer = app.model.Offer
OfferAlias = aliased(Offer, name='offer_alias')
Offerer = app.model.Offerer
Thing = app.model.Thing
Venue = app.model.Venue

mediation_filter = Mediation.thumbCount != None
def with_event_mediation(source_ids):
    def inner(query):
        return query.outerjoin(EventOccurence)\
                    .filter(~EventOccurence.eventId.in_(source_ids))\
                    .join(OfferAlias)\
                    .filter((OfferAlias.eventOccurenceId == EventOccurence.id) &
                            (OfferAlias.bookingLimitDatetime > datetime.now()))\
                    .outerjoin(Event)\
                    .filter((Event.mediations.any(mediation_filter)))
    return inner

def with_thing_mediation(source_ids):
    def inner(query):
        return query.outerjoin(Thing)\
                    .filter(~Thing.id.in_(source_ids))\
                    .filter((Thing.mediations.any(mediation_filter)))
    return inner

def with_event(query):
    return query.outerjoin(EventOccurence)\
                .outerjoin(Event)\
                .filter(Event.thumbCount > 0)

def with_thing(query):
    return query.outerjoin(Thing)\
                .filter(Thing.thumbCount > 0)

# FILTER OFFERS THAT ARE THE CLOSEST
def with_distance(latitude, longitude):
    distance_order_by = func.sqrt(
        func.pow(Venue.latitude - latitude, 2) +
        func.pow(Venue.longitude - longitude, 2)
    )
    def inner(query):
        return query.join(Offerer)\
                    .join(Venue)\
                    .order_by(distance_order_by)
    return inner


# FILTER OFFERS THAT ARE IN THE RIGHT "DEPARTEMENTS"
def with_departement_codes(departement_codes):
    def inner(query):
        return query.join(Offerer)\
                    .join(Venue)\
                    .filter_by(Venue.postCode in departement_codes)
    return inner


# FILTER OFFER WITH ONE OFFER PER EVENT
# THE ONE THAT IS WITH THE SOONER EVENT OCCURENCE
row_number_column = func.row_number()\
                        .over(partition_by=Event.id,
                              order_by=desc(EventOccurence.beginningDatetime))\
                        .label('row_number')
def with_event_deduplication(query):
    return query.add_column(row_number_column)\
                .from_self()\
                .filter(row_number_column == 1)
