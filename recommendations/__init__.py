""" recommendations """
from flask import current_app as app
from datetime import datetime, timedelta
from random import randint

from utils.attr_dict import AttrDict
from utils.content import get_source
from utils.includes import offers_includes

UserMediation = app.model.UserMediation
UserMediationOffer = app.model.UserMediationOffer

app.recommendations = AttrDict()

from recommendations.offers import get_offers

def create_recommendations(user, limit=3):
    if user.is_authenticated:
        first_um = UserMediation.query.filter_by(user=user)\
                                .first()
    offers = get_offers(user, limit)
    for (index, offer) in enumerate(offers):

        # CREATE
        um = UserMediation()
        um.user = user
        um.validUntilDate = datetime.now() + timedelta(days=2) # TODO: make this smart based on event dates, etc.

        # LOOK IF OFFER HAS (THING OR EVENT)(IE SOURCE) WITH MEDIATIONS
        # AND PICK ONE OF THEM
        dict_offer = offer._asdict(include=offers_includes)
        source = get_source(None, dict_offer)
        mediations = source['mediations']
        mediation_id = None
        if mediations:
            mediation_index = randint(0, len(mediations) - 1)
            mediation_id = mediations[mediation_index]['id']
            um.mediationId = mediation_id

        # ADD A TAG FOR THE FIRST UM
        if first_um is None and index == 0:
            um.isFirst = True

        # SAVE AND DO THE UM OFFER JOIN
        app.model.PcObject.check_and_save(um)
        umo = UserMediationOffer()
        umo.offerId = offer.id
        umo.userMediation = um
        app.model.PcObject.check_and_save(umo)
