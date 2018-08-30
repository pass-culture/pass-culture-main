from models import Recommendation, Mediation


def find_unseen_tutorials_for_user(seen_recommendation_ids, user):
    return Recommendation.query.join(Mediation) \
        .filter(
        (Mediation.tutoIndex != None)
        & (Recommendation.user == user)
        & ~Recommendation.id.in_(seen_recommendation_ids)
    ) \
        .order_by(Mediation.tutoIndex) \
        .all()


def count_read_recommendations_for_user(user):
    return Recommendation.query \
        .filter((Recommendation.user == user) & (Recommendation.dateRead != None)) \
        .count()
