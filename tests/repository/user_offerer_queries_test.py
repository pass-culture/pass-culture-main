import pytest
from sqlalchemy.orm.exc import MultipleResultsFound

from pcapi.core.offerers.models import Offerer
from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_product_with_event_subcategory
from pcapi.model_creators.specific_creators import create_product_with_thing_subcategory
from pcapi.models import Offer
from pcapi.models import UserOfferer
from pcapi.models import Venue
from pcapi.repository import repository
from pcapi.repository.user_offerer_queries import filter_query_where_user_is_user_offerer_and_is_validated
from pcapi.repository.user_offerer_queries import find_one_or_none_by_user_id


@pytest.mark.usefixtures("db_session")
def test_find_one_or_none_by_user_id_should_return_one_user_offerer_with_same_user_id(app):
    # Given
    pro = users_factories.ProFactory(email="offerer@email.com")
    offerer = create_offerer(siren="123456789")
    user_offerer = create_user_offerer(pro, offerer)
    repository.save(user_offerer)

    # When
    first_user_offerer = find_one_or_none_by_user_id(pro.id)

    # Then
    assert isinstance(first_user_offerer, UserOfferer)
    assert first_user_offerer.id == user_offerer.id


@pytest.mark.usefixtures("db_session")
def test_find_one_or_none_by_user_id_raises_exception_when_several_are_found(app):
    # Given
    pro = users_factories.ProFactory(email="offerer@email.com")
    offerer1 = create_offerer(siren="123456789")
    offerer2 = create_offerer(siren="987654321")
    user_offerer1 = create_user_offerer(pro, offerer1)
    user_offerer2 = create_user_offerer(pro, offerer2)
    repository.save(user_offerer1, user_offerer2)

    # When
    with pytest.raises(MultipleResultsFound):
        find_one_or_none_by_user_id(pro.id)


@pytest.mark.usefixtures("db_session")
def test_find_one_or_none_by_user_id_should_return_none_user_offerer_when_none_are_found(app):
    # Given
    pro = users_factories.ProFactory(email="offerer@email.com")
    offerer = create_offerer(siren="123456789")
    repository.save(offerer)

    # When
    first_user_offerer = find_one_or_none_by_user_id(pro.id)

    # Then
    assert first_user_offerer is None


@pytest.mark.usefixtures("db_session")
def test_filter_query_where_user_is_user_offerer_and_is_validated(app):
    # Given
    pro = users_factories.ProFactory(email="offerer@email.com")
    offerer1 = create_offerer(siren="123456789")
    offerer2 = create_offerer(siren="987654321")
    offerer3 = create_offerer(siren="123456780")
    user_offerer1 = create_user_offerer(pro, offerer1)
    user_offerer2 = create_user_offerer(pro, offerer2)

    event1 = create_product_with_event_subcategory(event_name="Rencontre avec Jacques Martin")
    event2 = create_product_with_event_subcategory(event_name="Concert de contrebasse")
    thing1 = create_product_with_thing_subcategory(thing_name="Jacques la fripouille")
    thing2 = create_product_with_thing_subcategory(thing_name="Belle du Seigneur")
    venue1 = create_venue(offerer1, name="Bataclan", city="Paris", siret=offerer1.siren + "12345")
    venue2 = create_venue(offerer2, name="Librairie la Rencontre", city="Saint Denis", siret=offerer2.siren + "54321")
    venue3 = create_venue(
        offerer3, name="Une librairie du méchant concurrent gripsou", city="Saint Denis", siret=offerer3.siren + "54321"
    )
    offer1 = create_offer_with_event_product(venue=venue1, product=event1)
    offer2 = create_offer_with_event_product(venue=venue1, product=event2)
    offer3 = create_offer_with_thing_product(venue=venue2, product=thing1)
    offer4 = create_offer_with_thing_product(venue=venue3, product=thing2)

    repository.save(user_offerer1, user_offerer2, offerer3, offer1, offer2, offer3, offer4)

    # When
    offers = filter_query_where_user_is_user_offerer_and_is_validated(Offer.query.join(Venue).join(Offerer), pro).all()

    # Then
    offer_ids = [offer.id for offer in offers]
    assert offer1.id in offer_ids
    assert offer2.id in offer_ids
    assert offer3.id in offer_ids
    assert offer4.id not in offer_ids
