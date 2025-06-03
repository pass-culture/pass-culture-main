from pcapi.routes.apis import public_api
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.decorator import spectree_serialize


class StrongTimeBody(BaseModel):
    offerId: int
    matchScore: int


@public_api.route("/strong-time", methods=["POST"])
@spectree_serialize(on_success_status=200)
def post_strong_time(body: StrongTimeBody) -> int:
    # offer: models.Offer = models.Offer.query.get(body.offerId)
    print(body)

    return 200
