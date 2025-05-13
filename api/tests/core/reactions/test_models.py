import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.reactions import factories
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
def test_like_insertion_increment_product_count():
    product = offers_factories.ProductFactory()
    factories.ReactionFactory.create(product=product, reactionType=ReactionTypeEnum.LIKE)

    assert product.likesCount == 1


@pytest.mark.usefixtures("db_session")
def test_like_deletion_decrement_product_count():
    product = offers_factories.ProductFactory()

    like = factories.ReactionFactory.create(product=product, reactionType=ReactionTypeEnum.LIKE)
    assert product.likesCount == 1

    db.session.delete(like)
    db.session.refresh(product)

    assert product.likesCount == 0


@pytest.mark.usefixtures("db_session")
def test_update_to_like_increments_product_count():
    product = offers_factories.ProductFactory()

    like = factories.ReactionFactory.create(product=product, reactionType=ReactionTypeEnum.DISLIKE)
    assert product.likesCount == 0

    like.reactionType = ReactionTypeEnum.LIKE
    db.session.commit()

    assert product.likesCount == 1


@pytest.mark.usefixtures("db_session")
def test_like_update_decrement_product_count():
    product = offers_factories.ProductFactory()

    like = factories.ReactionFactory.create(product=product, reactionType=ReactionTypeEnum.LIKE)
    assert product.likesCount == 1

    like.reactionType = ReactionTypeEnum.NO_REACTION
    db.session.commit()

    assert product.likesCount == 0
