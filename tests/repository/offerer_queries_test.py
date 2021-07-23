from datetime import date
from datetime import datetime

import pytest

from pcapi.core.offerers.models import Offerer
from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import Venue
from pcapi.repository import repository
from pcapi.repository.offerer_queries import filter_offerers_with_keywords_string
from pcapi.repository.offerer_queries import find_by_id
from pcapi.repository.offerer_queries import find_new_offerer_user_email
from pcapi.repository.offerer_queries import get_offerers_by_date_validated


class OffererQueriesTest:
    @pytest.mark.usefixtures("db_session")
    def test_find_by_id_returns_the_right_offerer(self, app):
        # Given
        offerer_id = 52325
        searched_offerer = create_offerer(idx=offerer_id, name="My sweet offerer", siren="123456789")
        other_offerer = create_offerer(siren="987654321")
        repository.save(searched_offerer, other_offerer)

        # When
        offerer = find_by_id(offerer_id)

        # Then
        assert offerer.name == "My sweet offerer"


@pytest.mark.usefixtures("db_session")
def test_find_email_of_user_offerer_should_returns_email(app):
    # Given
    offerer = create_offerer()
    pro_user = users_factories.ProFactory(email="pro@example.com")
    user_offerer = create_user_offerer(pro_user, offerer)

    repository.save(user_offerer)

    # When
    result = find_new_offerer_user_email(offerer.id)

    # Then
    assert result == "pro@example.com"


@pytest.mark.usefixtures("db_session")
def test_find_filtered_offerers_with_one_keyword_at_venue_public_name_level(app):
    # given
    offerer_with_only_virtual_venue_with_offer = create_offerer(siren="123456785")
    offerer_with_only_virtual_venue_without_offer = create_offerer(siren="123456786")
    offerer_with_both_venues_none_offer = create_offerer(siren="123456781")
    offerer_with_both_venues_offer_on_both = create_offerer(siren="123456782")
    offerer_with_both_venues_offer_on_virtual = create_offerer(siren="123456783")
    offerer_with_both_venues_offer_on_not_virtual = create_offerer(siren="123456784")

    virtual_venue_with_offer_1 = create_venue(offerer_with_only_virtual_venue_with_offer, is_virtual=True, siret=None)
    virtual_venue_without_offer_1 = create_venue(
        offerer_with_only_virtual_venue_without_offer, is_virtual=True, siret=None
    )
    virtual_venue_without_offer_2 = create_venue(offerer_with_both_venues_none_offer, is_virtual=True, siret=None)
    venue_without_offer_2 = create_venue(offerer_with_both_venues_none_offer, siret="12345678112345")
    virtual_venue_with_offer_3 = create_venue(
        offerer_with_both_venues_offer_on_both, is_virtual=True, siret=None, public_name="chouette lieu de ouf"
    )
    venue_with_offer_3 = create_venue(
        offerer_with_both_venues_offer_on_both, siret="12345678212345", public_name="chouette lieu de ouf"
    )
    virtual_venue_with_offer_4 = create_venue(
        offerer_with_both_venues_offer_on_virtual, is_virtual=True, siret=None, public_name="chouette lieu de ouf"
    )
    venue_without_offer_4 = create_venue(
        offerer_with_both_venues_offer_on_virtual, siret="12345678312345", public_name="chouette lieu de ouf"
    )
    virtual_venue_without_offer_5 = create_venue(
        offerer_with_both_venues_offer_on_not_virtual, is_virtual=True, siret=None, public_name="chouette lieu de ouf"
    )
    venue_with_offer_5 = create_venue(
        offerer_with_both_venues_offer_on_not_virtual, siret="12345678412345", public_name="chouette lieu de ouf"
    )

    offer_1 = create_offer_with_thing_product(virtual_venue_with_offer_1, url="http://url.com")
    offer_2 = create_offer_with_thing_product(virtual_venue_with_offer_3, url="http://url.com")
    offer_3 = create_offer_with_event_product(venue_with_offer_3)
    offer_4 = create_offer_with_thing_product(virtual_venue_with_offer_4, url="http://url.com")
    offer_5 = create_offer_with_event_product(venue_with_offer_5)

    repository.save(
        offer_1,
        offer_2,
        offer_3,
        offer_4,
        offer_5,
        virtual_venue_without_offer_1,
        virtual_venue_without_offer_2,
        virtual_venue_without_offer_5,
        venue_without_offer_2,
        venue_without_offer_4,
    )

    # when
    offerers = filter_offerers_with_keywords_string(Offerer.query.join(Venue), "chouette")

    # then
    assert offerer_with_only_virtual_venue_with_offer not in offerers
    assert offerer_with_only_virtual_venue_without_offer not in offerers
    assert offerer_with_both_venues_none_offer not in offerers
    assert offerer_with_both_venues_offer_on_both in offerers
    assert offerer_with_both_venues_offer_on_virtual in offerers
    assert offerer_with_both_venues_offer_on_not_virtual in offerers


@pytest.mark.usefixtures("db_session")
def test_find_filtered_offerers_with_one_partial_keyword_at_venue_public_name_level(app):
    # given
    offerer_with_only_virtual_venue_with_offer = create_offerer(siren="123456785")
    offerer_with_only_virtual_venue_without_offer = create_offerer(siren="123456786")
    offerer_with_both_venues_none_offer = create_offerer(siren="123456781")
    offerer_with_both_venues_offer_on_both = create_offerer(siren="123456782")
    offerer_with_both_venues_offer_on_virtual = create_offerer(siren="123456783")
    offerer_with_both_venues_offer_on_not_virtual = create_offerer(siren="123456784")

    virtual_venue_with_offer_1 = create_venue(offerer_with_only_virtual_venue_with_offer, is_virtual=True, siret=None)
    virtual_venue_without_offer_1 = create_venue(
        offerer_with_only_virtual_venue_without_offer, is_virtual=True, siret=None
    )
    virtual_venue_without_offer_2 = create_venue(offerer_with_both_venues_none_offer, is_virtual=True, siret=None)
    venue_without_offer_2 = create_venue(offerer_with_both_venues_none_offer, siret="12345678112345")
    virtual_venue_with_offer_3 = create_venue(
        offerer_with_both_venues_offer_on_both, is_virtual=True, siret=None, public_name="chouette lieu de ouf"
    )
    venue_with_offer_3 = create_venue(
        offerer_with_both_venues_offer_on_both, siret="12345678212345", public_name="chouette lieu de ouf"
    )
    virtual_venue_with_offer_4 = create_venue(
        offerer_with_both_venues_offer_on_virtual, is_virtual=True, siret=None, public_name="chouette lieu de ouf"
    )
    venue_without_offer_4 = create_venue(
        offerer_with_both_venues_offer_on_virtual, siret="12345678312345", public_name="chouette lieu de ouf"
    )
    virtual_venue_without_offer_5 = create_venue(
        offerer_with_both_venues_offer_on_not_virtual, is_virtual=True, siret=None, public_name="chouette lieu de ouf"
    )
    venue_with_offer_5 = create_venue(
        offerer_with_both_venues_offer_on_not_virtual, siret="12345678412345", public_name="chouette lieu de ouf"
    )

    offer_1 = create_offer_with_thing_product(virtual_venue_with_offer_1, url="http://url.com")
    offer_2 = create_offer_with_thing_product(virtual_venue_with_offer_3, url="http://url.com")
    offer_3 = create_offer_with_event_product(venue_with_offer_3)
    offer_4 = create_offer_with_thing_product(virtual_venue_with_offer_4, url="http://url.com")
    offer_5 = create_offer_with_event_product(venue_with_offer_5)

    repository.save(
        offer_1,
        offer_2,
        offer_3,
        offer_4,
        offer_5,
        virtual_venue_without_offer_1,
        virtual_venue_without_offer_2,
        virtual_venue_without_offer_5,
        venue_without_offer_2,
        venue_without_offer_4,
    )

    # when
    offerers = filter_offerers_with_keywords_string(Offerer.query.join(Venue), "chou")

    # then
    assert offerer_with_only_virtual_venue_with_offer not in offerers
    assert offerer_with_only_virtual_venue_without_offer not in offerers
    assert offerer_with_both_venues_none_offer not in offerers
    assert offerer_with_both_venues_offer_on_both in offerers
    assert offerer_with_both_venues_offer_on_virtual in offerers
    assert offerer_with_both_venues_offer_on_not_virtual in offerers


@pytest.mark.usefixtures("db_session")
def test_find_filtered_offerers_with_several_keywords_at_venue_public_name_level(app):
    # given
    offerer_with_only_virtual_venue_with_offer = create_offerer(siren="123456785")
    offerer_with_only_virtual_venue_without_offer = create_offerer(siren="123456786")
    offerer_with_both_venues_none_offer = create_offerer(siren="123456781")
    offerer_with_both_venues_offer_on_both = create_offerer(siren="123456782")
    offerer_with_both_venues_offer_on_virtual = create_offerer(siren="123456783")
    offerer_with_both_venues_offer_on_not_virtual = create_offerer(siren="123456784")

    virtual_venue_with_offer_1 = create_venue(offerer_with_only_virtual_venue_with_offer, is_virtual=True, siret=None)
    virtual_venue_without_offer_1 = create_venue(
        offerer_with_only_virtual_venue_without_offer, is_virtual=True, siret=None
    )
    virtual_venue_without_offer_2 = create_venue(offerer_with_both_venues_none_offer, is_virtual=True, siret=None)
    venue_without_offer_2 = create_venue(offerer_with_both_venues_none_offer, siret="12345678112345")
    virtual_venue_with_offer_3 = create_venue(
        offerer_with_both_venues_offer_on_both, is_virtual=True, siret=None, public_name="chouette lieu de ouf"
    )
    venue_with_offer_3 = create_venue(
        offerer_with_both_venues_offer_on_both, siret="12345678212345", public_name="chouette lieu de ouf"
    )
    virtual_venue_with_offer_4 = create_venue(
        offerer_with_both_venues_offer_on_virtual, is_virtual=True, siret=None, public_name="chouette lieu de ouf"
    )
    venue_without_offer_4 = create_venue(
        offerer_with_both_venues_offer_on_virtual, siret="12345678312345", public_name="chouette lieu de ouf"
    )
    virtual_venue_without_offer_5 = create_venue(
        offerer_with_both_venues_offer_on_not_virtual, is_virtual=True, siret=None, public_name="chouette lieu de ouf"
    )
    venue_with_offer_5 = create_venue(
        offerer_with_both_venues_offer_on_not_virtual, siret="12345678412345", public_name="chouette lieu de ouf"
    )

    offer_1 = create_offer_with_thing_product(virtual_venue_with_offer_1, url="http://url.com")
    offer_2 = create_offer_with_thing_product(virtual_venue_with_offer_3, url="http://url.com")
    offer_3 = create_offer_with_event_product(venue_with_offer_3)
    offer_4 = create_offer_with_thing_product(virtual_venue_with_offer_4, url="http://url.com")
    offer_5 = create_offer_with_event_product(venue_with_offer_5)

    repository.save(
        offer_1,
        offer_2,
        offer_3,
        offer_4,
        offer_5,
        virtual_venue_without_offer_1,
        virtual_venue_without_offer_2,
        virtual_venue_without_offer_5,
        venue_without_offer_2,
        venue_without_offer_4,
    )

    # when
    offerers = filter_offerers_with_keywords_string(Offerer.query.join(Venue), "chouette ouf")

    # then
    assert offerer_with_only_virtual_venue_with_offer not in offerers
    assert offerer_with_only_virtual_venue_without_offer not in offerers
    assert offerer_with_both_venues_none_offer not in offerers
    assert offerer_with_both_venues_offer_on_both in offerers
    assert offerer_with_both_venues_offer_on_virtual in offerers
    assert offerer_with_both_venues_offer_on_not_virtual in offerers


@pytest.mark.usefixtures("db_session")
def test_find_filtered_offerers_with_several_partial_keywords_at_venue_public_name_level(app):
    # given
    offerer_with_only_virtual_venue_with_offer = create_offerer(siren="123456785")
    offerer_with_only_virtual_venue_without_offer = create_offerer(siren="123456786")
    offerer_with_both_venues_none_offer = create_offerer(siren="123456781")
    offerer_with_both_venues_offer_on_both = create_offerer(siren="123456782")
    offerer_with_both_venues_offer_on_virtual = create_offerer(siren="123456783")
    offerer_with_both_venues_offer_on_not_virtual = create_offerer(siren="123456784")

    virtual_venue_with_offer_1 = create_venue(offerer_with_only_virtual_venue_with_offer, is_virtual=True, siret=None)
    virtual_venue_without_offer_1 = create_venue(
        offerer_with_only_virtual_venue_without_offer, is_virtual=True, siret=None
    )
    virtual_venue_without_offer_2 = create_venue(offerer_with_both_venues_none_offer, is_virtual=True, siret=None)
    venue_without_offer_2 = create_venue(offerer_with_both_venues_none_offer, siret="12345678112345")
    virtual_venue_with_offer_3 = create_venue(
        offerer_with_both_venues_offer_on_both, is_virtual=True, siret=None, public_name="chouette lieu de ouf"
    )
    venue_with_offer_3 = create_venue(
        offerer_with_both_venues_offer_on_both, siret="12345678212345", public_name="chouette lieu de ouf"
    )
    virtual_venue_with_offer_4 = create_venue(
        offerer_with_both_venues_offer_on_virtual, is_virtual=True, siret=None, public_name="chouette lieu de ouf"
    )
    venue_without_offer_4 = create_venue(
        offerer_with_both_venues_offer_on_virtual, siret="12345678312345", public_name="chouette lieu de ouf"
    )
    virtual_venue_without_offer_5 = create_venue(
        offerer_with_both_venues_offer_on_not_virtual, is_virtual=True, siret=None, public_name="chouette lieu de ouf"
    )
    venue_with_offer_5 = create_venue(
        offerer_with_both_venues_offer_on_not_virtual, siret="12345678412345", public_name="chouette lieu de ouf"
    )

    offer_1 = create_offer_with_thing_product(virtual_venue_with_offer_1, url="http://url.com")
    offer_2 = create_offer_with_thing_product(virtual_venue_with_offer_3, url="http://url.com")
    offer_3 = create_offer_with_event_product(venue_with_offer_3)
    offer_4 = create_offer_with_thing_product(virtual_venue_with_offer_4, url="http://url.com")
    offer_5 = create_offer_with_event_product(venue_with_offer_5)

    repository.save(
        offer_1,
        offer_2,
        offer_3,
        offer_4,
        offer_5,
        virtual_venue_without_offer_1,
        virtual_venue_without_offer_2,
        virtual_venue_without_offer_5,
        venue_without_offer_2,
        venue_without_offer_4,
    )

    # when
    offerers = filter_offerers_with_keywords_string(Offerer.query.join(Venue), "chou ou")

    # then
    assert offerer_with_only_virtual_venue_with_offer not in offerers
    assert offerer_with_only_virtual_venue_without_offer not in offerers
    assert offerer_with_both_venues_none_offer not in offerers
    assert offerer_with_both_venues_offer_on_both in offerers
    assert offerer_with_both_venues_offer_on_virtual in offerers
    assert offerer_with_both_venues_offer_on_not_virtual in offerers


@pytest.mark.usefixtures("db_session")
def test_get_offerers_by_date_validated(app):
    offerer1 = create_offerer(siren="123456789", validation_token=None, date_validated=datetime(2021, 6, 7, 15, 49))
    offerer2 = create_offerer(siren="123456788", validation_token=None, date_validated=datetime(2021, 6, 7, 23, 59, 59))
    offerer3 = create_offerer(siren="123456787", validation_token=None, date_validated=datetime(2021, 6, 8, 00, 00, 00))
    offerer4 = create_offerer(siren="123456786", validation_token=None, date_validated=datetime(2021, 6, 6, 11, 49))

    repository.save(offerer1, offerer2, offerer3, offerer4)

    assert get_offerers_by_date_validated(date(2021, 6, 7)) == [offerer1, offerer2]
    assert get_offerers_by_date_validated(date(2021, 6, 8)) == [offerer3]
    assert get_offerers_by_date_validated(date(2021, 6, 6)) == [offerer4]
