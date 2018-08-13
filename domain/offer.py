from repository import thing_queries


class InconsistentOffer(Exception):

    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return self.message


def check_digital_offer_consistency(offer, venue, find_thing=thing_queries.find_by_id):
    thing = find_thing(offer.thingId)

    if venue.isVirtual and not thing.url:
        raise InconsistentOffer('Offer.venue is virtual but Offer.thing does not have an URL')

    if not venue.isVirtual and thing.url:
        raise InconsistentOffer('Offer.venue is not virtual but Offer.thing has an URL')
