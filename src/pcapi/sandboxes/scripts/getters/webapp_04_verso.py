from pcapi.models import MediationSQLEntity, OfferSQLEntity, StockSQLEntity, UserSQLEntity, Product
from pcapi.models.recommendation import Recommendation
from pcapi.repository.user_queries import keep_only_webapp_users
from pcapi.sandboxes.scripts.utils.bookings import find_offer_compatible_with_bookings, \
    get_cancellable_bookings_for_user
from pcapi.sandboxes.scripts.utils.helpers import get_mediation_helper, \
    get_offer_helper, \
    get_beneficiary_helper, \
    get_recommendation_helper


def get_existing_webapp_user_with_at_least_one_recommendation():
   query = Recommendation.query.join(UserSQLEntity)
   query = keep_only_webapp_users(query)
   query = query.reset_joinpoint().join(OfferSQLEntity)

   recommendation = query.first()
   return {
       "user": get_beneficiary_helper(recommendation.user),
       "recommendation": get_recommendation_helper(recommendation)
   }


def get_existing_webapp_hnmm_user(return_as_dict=False):
    query = keep_only_webapp_users(UserSQLEntity.query)
    query = query.filter(UserSQLEntity.email.contains('93.has-no-more-money'))
    user = query.first()
    if return_as_dict == False:
        return user
    return {
        "user": get_beneficiary_helper(user)
    }


def get_existing_webapp_hbs_user():
    query = keep_only_webapp_users(UserSQLEntity.query)
    query = query.filter(UserSQLEntity.email.contains('has-booked-some'))
    user = query.first()
    return {
        "user": get_beneficiary_helper(user)
    }


def get_existing_event_offer_with_active_mediation_already_booked_but_cancellable_and_user_hnmm_93():
    offer_with_stock_id_tuples = OfferSQLEntity.query \
        .filter(OfferSQLEntity.mediations.any(MediationSQLEntity.isActive)) \
        .join(StockSQLEntity) \
        .filter(StockSQLEntity.beginningDatetime != None) \
        .add_columns(StockSQLEntity.id) \
        .all()
    user = get_existing_webapp_hnmm_user()
    bookings = get_cancellable_bookings_for_user(user)
    offer = find_offer_compatible_with_bookings(offer_with_stock_id_tuples, bookings)

    for mediation in offer.mediations:
        if mediation.isActive:
            return {
                "mediation": get_mediation_helper(mediation),
                "offer": get_offer_helper(offer),
                "user": get_beneficiary_helper(user)
            }


def get_existing_digital_offer_with_active_mediation_already_booked_and_user_hnmm_93():
    offer_with_stock_id_tuples = OfferSQLEntity.query.outerjoin(Product) \
        .filter(OfferSQLEntity.mediations.any(MediationSQLEntity.isActive)) \
        .filter(Product.url != None) \
        .join(StockSQLEntity, (OfferSQLEntity.id == StockSQLEntity.offerId)) \
        .add_columns(StockSQLEntity.id) \
        .all()
    user = get_existing_webapp_hnmm_user()
    bookings = get_cancellable_bookings_for_user(user)
    offer = find_offer_compatible_with_bookings(offer_with_stock_id_tuples, bookings)

    for mediation in offer.mediations:
        if mediation.isActive:
            return {
                "mediation": get_mediation_helper(mediation),
                "offer": get_offer_helper(offer),
                "user": get_beneficiary_helper(user)
            }
