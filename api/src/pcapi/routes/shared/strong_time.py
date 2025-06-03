from pcapi.core.criteria import models as criterion_models
from pcapi.core.offers import models
from pcapi.models import db
from pcapi.routes.apis import public_api
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.decorator import spectree_serialize


class StrongTimeBody(BaseModel):
    offerId: int
    tagName: str
    matchScore: int
    scoreReason: str


@public_api.route("/strong-time", methods=["POST"])
@spectree_serialize(on_success_status=204)
def post_strong_time(body: StrongTimeBody) -> int:
    offer: models.Offer = models.Offer.query.get(body.offerId)

    criterion: criterion_models.Criterion = criterion_models.Criterion.query.filter_by(name=body.tagName).one()

    # tag the offer
    link = (
        db.session.query(criterion_models.OfferCriterion)
        .filter_by(offerId=offer.id, criterionId=criterion.id)
        .one_or_none()
    )
    if link is None:
        db.session.add(criterion_models.OfferCriterion(offerId=offer.id, criterionId=criterion.id))

    offer.extraData["matchScore"] = body.matchScore
    offer.extraData["scoreReason"] = body.scoreReason

    db.session.commit()

    print(f"Found offer {offer.id} and tag {criterion.id}, {criterion.name}")
