from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy_utils import refresh_materialized_view

from models import DiscoveryView
from models.db import Model, db
from repository.discovery_view_queries import _create_function_offer_has_at_least_one_bookable_stock, \
    _create_function_offer_has_at_least_one_active_mediation, _create_function_event_is_in_less_than_10_days, \
    _create_function_get_offer_score


class DiscoveryViewV3(Model):
    __tablename__ = 'discovery_view_v3'

    venueId = Column(BigInteger, ForeignKey('venue.id'))

    mediationId = Column(BigInteger, ForeignKey('mediation.id'))

    id = Column(BigInteger, primary_key=True)

    type = Column(String(50))

    url = Column(String(255))

    offerDiscoveryOrder = Column(Integer)

    name = Column(String(140))

    isNational = Column(Boolean)
