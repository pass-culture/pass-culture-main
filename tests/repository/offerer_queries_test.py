import secrets

import pytest

from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import Offerer
from pcapi.models import VenueSQLEntity
from pcapi.repository import repository
from pcapi.repository.offerer_queries import filter_offerers_with_keywords_string
from pcapi.repository.offerer_queries import find_by_id
from pcapi.repository.offerer_queries import find_first_by_user_offerer_id
from pcapi.repository.offerer_queries import find_new_offerer_user_email
from pcapi.repository.user_queries import find_all_emails_of_user_offerers_admins


class OffererQueriesTest:
    @pytest.mark.usefixtures("db_session")
    def test_find_by_id_returns_the_right_offerer(self, app):
        # Given
        id = 52325
        searched_offerer = create_offerer(idx=id, name="My sweet offerer", siren="123456789")
        other_offerer = create_offerer(siren="987654321")
        repository.save(searched_offerer, other_offerer)

        # When
        offerer = find_by_id(id)

        # Then
        assert offerer.name == "My sweet offerer"


@pytest.mark.usefixtures("db_session")
def test_find_all_emails_of_user_offerers_admins_returns_list_of_user_emails_having_user_offerer_with_admin_rights_on_offerer(
    app,
):
    # Given
    offerer = create_offerer()
    user_admin1 = create_user(email="admin1@offerer.com")
    user_admin2 = create_user(email="admin2@offerer.com")
    user_editor = create_user(email="editor@offerer.com")
    user_admin_not_validated = create_user(email="admin_not_validated@offerer.com")
    user_random = create_user(email="random@user.com")
    user_offerer_admin1 = create_user_offerer(user_admin1, offerer, is_admin=True)
    user_offerer_admin2 = create_user_offerer(user_admin2, offerer, is_admin=True)
    user_offerer_admin_not_validated = create_user_offerer(
        user_admin_not_validated, offerer, validation_token=secrets.token_urlsafe(20), is_admin=True
    )
    user_offerer_editor = create_user_offerer(user_editor, offerer, is_admin=False)
    repository.save(
        user_random, user_offerer_admin1, user_offerer_admin2, user_offerer_admin_not_validated, user_offerer_editor
    )

    # When
    emails = find_all_emails_of_user_offerers_admins(offerer.id)

    # Then
    assert set(emails) == {"admin1@offerer.com", "admin2@offerer.com"}
    assert type(emails) == list


@pytest.mark.usefixtures("db_session")
def test_find_email_of_user_offerer_should_returns_email(app):
    # Given
    offerer = create_offerer()
    pro_user = create_user(email="pro@example.com")
    user_offerer = create_user_offerer(pro_user, offerer)

    repository.save(pro_user, user_offerer)

    # When
    result = find_new_offerer_user_email(offerer.id)

    # Then
    assert result == "pro@example.com"



@pytest.mark.usefixtures("db_session")
def test_find_first_by_user_offerer_id_returns_the_first_offerer_that_was_created(app):
    # given
    user = create_user()
    offerer1 = create_offerer(name="offerer1", siren="123456789")
    offerer2 = create_offerer(name="offerer2", siren="789456123")
    offerer3 = create_offerer(name="offerer2", siren="987654321")
    user_offerer1 = create_user_offerer(user, offerer1)
    user_offerer2 = create_user_offerer(user, offerer2)
    repository.save(user_offerer1, user_offerer2, offerer3)

    # when
    offerer = find_first_by_user_offerer_id(user_offerer1.id)

    # then
    assert offerer.id == offerer1.id


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
    offerers = filter_offerers_with_keywords_string(Offerer.query.join(VenueSQLEntity), "chouette")

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
    offerers = filter_offerers_with_keywords_string(Offerer.query.join(VenueSQLEntity), "chou")

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
    offerers = filter_offerers_with_keywords_string(Offerer.query.join(VenueSQLEntity), "chouette ouf")

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
    offerers = filter_offerers_with_keywords_string(Offerer.query.join(VenueSQLEntity), "chou ou")

    # then
    assert offerer_with_only_virtual_venue_with_offer not in offerers
    assert offerer_with_only_virtual_venue_without_offer not in offerers
    assert offerer_with_both_venues_none_offer not in offerers
    assert offerer_with_both_venues_offer_on_both in offerers
    assert offerer_with_both_venues_offer_on_virtual in offerers
    assert offerer_with_both_venues_offer_on_not_virtual in offerers
