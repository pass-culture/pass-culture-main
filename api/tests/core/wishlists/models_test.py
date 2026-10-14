import pytest
import sqlalchemy as sa

from pcapi.core.artist import factories as artist_factories
from pcapi.core.discoveries import models as discoveries_models
from pcapi.core.users import factories as users_factories
from pcapi.core.wishlists import models
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


def test_share_token_is_generated_and_unique():
    user = users_factories.UserFactory()
    first = models.Wishlist(user=user, name="A")
    second = models.Wishlist(user=user, name="B")
    db.session.add_all([first, second])
    db.session.flush()

    assert first.share_token and second.share_token
    assert first.share_token != second.share_token
    assert first.visibility == models.WishlistVisibility.PRIVATE


def test_blank_name_is_rejected():
    db.session.add(models.Wishlist(user=users_factories.UserFactory(), name="   "))

    with pytest.raises(sa.exc.IntegrityError):
        db.session.flush()
    db.session.rollback()


@pytest.mark.parametrize("target", ["none", "both"])
def test_item_requires_exactly_one_target(target):
    wishlist = models.Wishlist(user=users_factories.UserFactory(), name="A")
    item = models.WishlistItem(wishlist=wishlist, position=0)
    if target == "both":
        item.artist = artist_factories.ArtistFactory()
        item.work = discoveries_models.Work(title="W", media_type=discoveries_models.WorkMediaType.BOOK)
    db.session.add(item)

    with pytest.raises(sa.exc.IntegrityError):
        db.session.flush()
    db.session.rollback()
