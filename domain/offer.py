from repository import thing_queries, venue_queries


class InconsistentOffer(Exception):

    def __init__(self, message=''):
        self.message = 'InconsistentOffer : %s' % message

    def __str__(self):
        return self.message


def check_digital_offer_consistency(
        offer,
        find_thing=thing_queries.find_by_id,
        find_venue=venue_queries.find_by_id
):
    thing = find_thing(offer.thingId)
    venue = find_venue(offer.venueId)

    if not venue:
        raise InconsistentOffer('Offer.venue is unknown')

    if venue.isVirtual and not thing.url:
        raise InconsistentOffer('Offer.venue is virtual but Offer.thing does not have an URL')

    if not venue.isVirtual and thing.url:
        raise InconsistentOffer('Offer.venue is not virtual but Offer.thing has an URL')
