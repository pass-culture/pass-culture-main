from typing import Optional, List

from flask import request, jsonify
from flask_login import current_user

from models import UserSQLEntity, Offer
from repository.offer_queries import build_find_offers_with_filter_parameters
from routes.serialization import as_dict
from utils.includes import OFFER_INCLUDES


def get_paginated_offers_for_offerer_venue_and_keywords(user: UserSQLEntity,
                                                        offerer_id: int,
                                                        pagination_limit: int,
                                                        venue_id: int,
                                                        page: Optional[int],
                                                        keywords: str) -> str:
    query = build_find_offers_with_filter_parameters(
        user=user,
        offerer_id=offerer_id,
        venue_id=venue_id,
        keywords_string=keywords,
    )
    query = query.paginate(page, per_page=int(pagination_limit), error_out=False)
    results = query.items
    total = query.total

    return serialize_paginated_offers_list(results, total)


def serialize_paginated_offers_list(results: List[Offer], total: int) -> str:
    response = jsonify([as_dict(offer, includes=OFFER_INCLUDES) for offer in results])
    response.headers['Total-Data-Count'] = total
    response.headers['Access-Control-Expose-Headers'] = 'Total-Data-Count'
    return response
