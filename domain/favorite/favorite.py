from models import OfferSQLEntity, MediationSQLEntity


class Favorite(object):
    def __init__(self, identifier: int, mediation: MediationSQLEntity, offer: OfferSQLEntity):
        self.identifier = identifier
        self.mediation = mediation
        self.offer = offer

    @property
    def thumb_url(self) -> str:
        if self.mediation:
            return self.mediation.thumbUrl
        return self.offer.product.thumbUrl
