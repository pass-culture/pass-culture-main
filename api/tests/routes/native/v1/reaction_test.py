import pytest

from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class PostReactionTest:
    def test_should_be_logged_in_to_post_reaction(self, client):
        with assert_num_queries(0):
            response = client.post("/native/v1/reaction", json={})
        assert response.status_code == 400

    def test_post_new_like_reaction(self, client):
        user = users_factories.BeneficiaryFactory()
        offer = OfferFactory()
        client.with_token(user.email)

        with assert_num_queries(4):
            # SELECT offer, user, reaction
            # INSERT reaction
            response = client.post("/native/v1/reaction", json={"offerId": offer.id, "reactionType": "LIKE"})
        reaction = user.reactions[0]

        assert response.status_code == 204
        assert reaction.reactionType == ReactionTypeEnum.LIKE

    def test_post_new_dislike_reaction(self, client):
        user = users_factories.BeneficiaryFactory()
        offer = OfferFactory()
        client.with_token(user.email)

        with assert_num_queries(4):
            # SELECT offer, user, reaction
            # INSERT reaction
            response = client.post("/native/v1/reaction", json={"offerId": offer.id, "reactionType": "DISLIKE"})
        reaction = user.reactions[0]

        assert response.status_code == 204
        assert reaction.reactionType == ReactionTypeEnum.DISLIKE

    def test_edit_reaction(self, client):
        user = users_factories.BeneficiaryFactory()
        offer = OfferFactory()
        client.with_token(user.email)

        with assert_num_queries(4):
            # SELECT offer, user, reaction
            # INSERT reaction
            response = client.post("/native/v1/reaction", json={"offerId": offer.id, "reactionType": "LIKE"})
        reaction = user.reactions[0]

        assert response.status_code == 204
        assert reaction.reactionType == ReactionTypeEnum.LIKE

        response = client.post("/native/v1/reaction", json={"offerId": offer.id, "reactionType": "DISLIKE"})
        reaction = user.reactions[0]

        assert response.status_code == 204
        assert reaction.reactionType == ReactionTypeEnum.DISLIKE

    def test_post_reaction_to_product(self, client):
        user = users_factories.BeneficiaryFactory()
        product = ProductFactory()
        offer = OfferFactory(product=product)
        client.with_token(user.email)

        with assert_num_queries(4):
            # SELECT offer, user, reaction
            # INSERT reaction
            response = client.post("/native/v1/reaction", json={"offerId": offer.id, "reactionType": "LIKE"})
        reaction = user.reactions[0]

        assert response.status_code == 204
        assert reaction.reactionType == ReactionTypeEnum.LIKE
        assert reaction.product == product
