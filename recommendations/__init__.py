""" recommendations """
from flask import current_app as app
from datetime import datetime, timedelta

from utils.attr_dict import AttrDict

UserMediation = app.model.UserMediation
UserMediationOffer = app.model.UserMediationOffer

app.recommendations = AttrDict()

from recommendations.offers import get_offers

def get_recommendations(user, limit=3):
    if user.is_authenticated:
        first_um = UserMediation.query.filter_by(user=user)\
                                .first()
    offers = get_offers(user, limit)
    print('offers.count', offers.count())
    for (index, offer) in enumerate(offers):
        um = UserMediation()
        um.user = user
        um.validUntilDate = datetime.now() + timedelta(days=2) # TODO: make this smart based on event dates, etc.
        # add a tag for the first item
        if first_um is None and index == 0:
            um.isFirst = True
        umo = UserMediationOffer()
        umo.offer = offer
        umo.userMediation = um
        app.model.PcObject.check_and_save(umo)

app.recommendations.get = get_recommendations
