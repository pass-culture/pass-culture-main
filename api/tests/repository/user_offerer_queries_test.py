import pytest
from sqlalchemy.orm.exc import MultipleResultsFound

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.users import factories as users_factories
from pcapi.repository.user_offerer_queries import filter_query_where_user_is_user_offerer_and_is_validated
from pcapi.repository.user_offerer_queries import find_one_or_none_by_user_id


@pytest.mark.usefixtures("db_session")
def test_find_one_or_none_by_user_id_should_return_one_user_offerer_with_same_user_id(app):
    pro = users_factories.ProFactory()
    user_offerer = offerers_factories.UserOffererFactory(user=pro)

    assert find_one_or_none_by_user_id(pro.id) == user_offerer


@pytest.mark.usefixtures("db_session")
def test_find_one_or_none_by_user_id_raises_exception_when_several_are_found():
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro)
    offerers_factories.UserOffererFactory(user=pro)

    with pytest.raises(MultipleResultsFound):
        find_one_or_none_by_user_id(pro.id)


@pytest.mark.usefixtures("db_session")
def test_find_one_or_none_by_user_id_should_return_none_user_offerer_when_none_are_found():
    pro = users_factories.ProFactory()
    assert find_one_or_none_by_user_id(pro.id) is None


@pytest.mark.usefixtures("db_session")
def test_filter_query_where_user_is_user_offerer_and_is_validated():
    # Given
    offer1 = offers_factories.OfferFactory()
    offer2 = offers_factories.OfferFactory()
    offer3 = offers_factories.OfferFactory()
    offerer1 = offer1.venue.managingOfferer
    offerer2 = offer2.venue.managingOfferer
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer1)
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer2)

    # When
    base_query = Offer.query.join(Venue).join(Offerer)
    offers = filter_query_where_user_is_user_offerer_and_is_validated(base_query, pro).all()

    # Then
    assert offer1 in offers
    assert offer2 in offers
    assert offer3 not in offers
