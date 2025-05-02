import pytest

from pcapi.core.chronicles.factories import ChronicleFactory
from pcapi.core.offers.factories import HeadlineOfferFactory
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.reactions.factories import ReactionFactory
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.models import db
from pcapi.scripts.init_product_counts.main import chronicles_count_query
from pcapi.scripts.init_product_counts.main import headlines_count_query
from pcapi.scripts.init_product_counts.main import likes_count_query
from pcapi.scripts.init_product_counts.main import update_product_count


@pytest.mark.usefixtures("db_session")
def test_chronicles_count() -> None:
    product_1 = ProductFactory()
    product_2 = ProductFactory()
    ChronicleFactory.create(products=[product_1, product_2])
    ChronicleFactory.create(products=[product_1])

    query = chronicles_count_query(product_1.id, product_2.id + 1).order_by("product_id")
    result = db.session.execute(query).all()

    assert result == [(product_1.id, 2), (product_2.id, 1)]


@pytest.mark.usefixtures("db_session")
def test_headlines_count() -> None:
    product_1 = ProductFactory()
    product_2 = ProductFactory()
    HeadlineOfferFactory(offer__product=product_1)
    HeadlineOfferFactory(offer__product=product_2)

    query = headlines_count_query(product_1.id, product_2.id + 1).order_by("product_id")
    result = db.session.execute(query).all()

    assert result == [(product_1.id, 1), (product_2.id, 1)]


@pytest.mark.usefixtures("db_session")
def test_likes_count() -> None:
    product = ProductFactory()
    ReactionFactory(product=product, reactionType=ReactionTypeEnum.LIKE)
    ReactionFactory(product=product, reactionType=ReactionTypeEnum.LIKE)
    ReactionFactory(product=product, reactionType=ReactionTypeEnum.NO_REACTION)

    query = likes_count_query(product.id, product.id + 1)
    result = db.session.execute(query).all()

    assert result == [(product.id, 2)]


def test_update_product_count() -> None:
    product_1 = ProductFactory()
    product_2 = ProductFactory()
    ReactionFactory(product=product_1, reactionType=ReactionTypeEnum.LIKE)
    ReactionFactory(product=product_1, reactionType=ReactionTypeEnum.LIKE)
    ReactionFactory(product=product_2, reactionType=ReactionTypeEnum.LIKE)
    ReactionFactory(product=product_2, reactionType=ReactionTypeEnum.LIKE)
    ReactionFactory(product=product_1, reactionType=ReactionTypeEnum.NO_REACTION)
    ReactionFactory(product=product_1, reactionType=ReactionTypeEnum.DISLIKE)

    product_1.likesCount = 0
    product_2.likesCount = 0

    update_product_count(likes_count_query(product_1.id, product_2.id + 1), "likesCount", True)

    assert product_1.likesCount == 2
    assert product_2.likesCount == 2
