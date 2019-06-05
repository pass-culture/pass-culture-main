""" recommendations stocks """
from itertools import cycle

from datetime import datetime
from random import randint
from sqlalchemy.orm import aliased
from typing import Optional, List, Tuple

from domain.departments import get_departement_codes_from_user
from models import Offer, Stock, Product
from models.offer_type import ProductType
from repository.offer_queries import get_active_offers
from utils.logger import logger


def get_offers_for_recommendations_discovery(limit=3, user=None, coords=None) -> List[Offer]:
    if not user or not user.is_authenticated():
        return []

    departement_codes = get_departement_codes_from_user(user)

    offers = get_active_offers(user=user,
                               departement_codes=departement_codes,
                               limit=limit)

    logger.debug(lambda: '(reco) final offers (events + things) count (%i)',
                 len(offers))

    return offers
