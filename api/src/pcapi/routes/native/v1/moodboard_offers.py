from pcapi.core.categories import subcategories_v2
from pcapi.core.categories import subcategories
from pcapi.core.offers.models import Offer, Product, Stock
from pcapi.serialization.decorator import spectree_serialize
from sqlalchemy import func, orm
import sqlalchemy as sa

from . import blueprint
from .serialization import moodboard_offers as serializers


@blueprint.native_v1.route("/moodboard_offers", methods=["GET"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=serializers.MoodboardOffersResponse)
def get_moodboard_offers(body: serializers.MoodboardOffersRequest) -> serializers.MoodboardOffersResponse:  # TODO: Secure this route
    user_deposit = 50 # TODO: get current user deposit
    
    query = Offer.query.options(
        orm.joinedload(Offer.venue),
        orm.joinedload(Offer.stocks),
        # orm.joinedload(Offer.product).joinedload(Product.extraData),
        # orm.joinedload(Offer.extraData)
    )
    
    # TODO: query on offer price under user remaining deposit
    
    if body.mood == serializers.Mood.FESTIVE:
        query = query.filter(Offer.isEvent)
        
        if body.theme == serializers.Theme.CLASSIC:
            pass
        elif body.theme == serializers.Theme.FUN:
            pass
        elif body.theme == serializers.Theme.SUMMER_VIBE:
            pass
        elif body.theme == serializers.Theme.DARK_MODE:
            pass

    elif body.mood == serializers.Mood.CHILL:
        query = query.filter(sa.not_(Offer.isEvent))
        
        if body.theme == serializers.Theme.NERD:
            query = query.filter(
                Offer.subcategoryId.in_(
                    subcategory.id for subcategory in subcategories_v2.ALL_SUBCATEGORIES
                    if subcategory.category.id in ["LIVRE", "MEDIA"]
                ),
            )
        elif body.theme == serializers.Theme.SCARY:
            pass
        elif body.theme == serializers.Theme.ROMANCE:
            query = query.filter(
                Offer.subcategoryId.in_(
                    subcategory.id for subcategory in subcategories_v2.ALL_SUBCATEGORIES
                    if subcategory.category.id in ["LIVRE"]
                )
            )
            # TODO: add filter on type erotic
        elif body.theme == serializers.Theme.CREATIVE:
            pass

    elif body.mood == serializers.Mood.LOVE:
        query = query.filter(Offer.isDuo)
        
        if body.theme == serializers.Theme.FUN:
            pass
        elif body.theme == serializers.Theme.ROMANCE:
            pass
        elif body.theme == serializers.Theme.ADVENTURE:
            pass
        elif body.theme == serializers.Theme.NERD:
            pass

    elif body.mood == serializers.Mood.ADVENTURE:
        if body.theme == serializers.Theme.MYSTERY:
            pass
        elif body.theme == serializers.Theme.NERD:
            pass
        elif body.theme == serializers.Theme.ADVENTURE:
            pass
        elif body.theme == serializers.Theme.CREATIVE:                
            query = query.filter(
                sa.or_(
                    Offer.subcategoryId.in_(
                        subcategory.id for subcategory in subcategories_v2.ALL_SUBCATEGORIES
                        if subcategory.category.id in ["PRATIQUE_ART", "BEAUX_ARTS"]
                    ),
                    sa.and_(
                        Offer.subcategoryId.in_(
                            subcategory.id for subcategory in subcategories_v2.ALL_SUBCATEGORIES
                            if subcategory.category.id in ["CINEMA"]
                        ),
                        # Offer.subcategory.native_category.genre_type.in_(["ANIMATION", "MUSIC"]),
                    ),
                    sa.and_(
                        Offer.subcategoryId.in_(
                            subcategory.id for subcategory in subcategories_v2.ALL_SUBCATEGORIES
                            if subcategory.category.id in ["LIVRE"]
                        ),
                        # Offer.subcategory.native_category.genre_type.in_(["Arts Culinaires", "Humour"]),
                    ),
                    sa.and_(
                        Offer.subcategoryId.in_(
                            subcategory.id for subcategory in subcategories_v2.ALL_SUBCATEGORIES
                            if subcategory.category.id == "SPECTACLE"
                        ),
                        # Offer.subcategory.native_category.genre_type.name == 200,
                    )
                )
            )
    
    return serializers.MoodboardOffersResponse(offers=query.limit(10).all())
