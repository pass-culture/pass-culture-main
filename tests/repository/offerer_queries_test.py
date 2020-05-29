import secrets
from datetime import datetime, timedelta

from models import Offerer, VenueSQLEntity, ThingType
from repository import repository
from repository.offerer_queries import find_first_by_user_offerer_id, \
    filter_offerers_with_keywords_string, find_by_id, count_offerer, count_offerer_with_stock, \
    count_offerer_by_departement, count_offerer_with_stock_by_departement, find_new_offerer_user_email
from repository.user_queries import find_all_emails_of_user_offerers_admins
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_stock, create_offerer, create_venue, \
    create_user_offerer
from tests.model_creators.specific_creators import create_stock_from_event_occurrence, create_stock_with_thing_offer, \
    create_offer_with_thing_product, create_offer_with_event_product, create_event_occurrence


class OffererQueriesTest:
    @clean_database
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


class CountOffererTest:
    @clean_database
    def test_return_zero_if_no_offerer(self, app):
        # When
        number_of_offerers = count_offerer()

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_return_1_if_offerer_with_user_offerer(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        repository.save(user_offerer)

        # When
        number_of_offerers = count_offerer()

        # Then
        assert number_of_offerers == 1

    @clean_database
    def test_return_0_if_offerer_without_user_offerer(self, app):
        # Given
        offerer = create_offerer()
        repository.save(offerer)

        # When
        number_of_offerers = count_offerer()

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_return_1_if_offerer_with_2_user_offerer(self, app):
        # Given
        user1 = create_user()
        user2 = create_user(email='em@ail.com')
        offerer = create_offerer()
        user_offerer1 = create_user_offerer(user1, offerer)
        user_offerer2 = create_user_offerer(user2, offerer)
        repository.save(user_offerer1, user_offerer2)

        # When
        number_of_offerers = count_offerer()

        # Then
        assert number_of_offerers == 1


class CountOffererByDepartementTest:
    @clean_database
    def test_return_zero_if_no_offerer(self, app):
        # When
        number_of_offerers = count_offerer_by_departement('54')

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_return_1_if_offerer_with_user_offerer(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        create_venue(offerer, postal_code='37160')
        user_offerer = create_user_offerer(user, offerer)
        repository.save(user_offerer)

        # When
        number_of_offerers = count_offerer_by_departement('37')

        # Then
        assert number_of_offerers == 1

    @clean_database
    def test_return_1_with_two_venues_but_only_one_in_the_departement(self, app):
        # Given
        user = create_user()
        offerer = create_offerer(siren='111111111')
        first_venue = create_venue(offerer, postal_code='37160', siret='11111111100001')
        second_venue = create_venue(offerer, postal_code='76130', siret='11111111100002')
        user_offerer = create_user_offerer(user, offerer)

        repository.save(user_offerer, first_venue, second_venue)

        # When
        number_of_offerers = count_offerer_by_departement('37')

        # Then
        assert number_of_offerers == 1

    @clean_database
    def test_return_0_if_offerer_without_venue(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='37160')
        user_offerer = create_user_offerer(user, offerer)
        repository.save(user_offerer)

        # When
        number_of_offerers = count_offerer_by_departement('36')

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_return_1_if_offerer_with_2_user_offerers_and_2_venues(self, app):
        # Given
        user1 = create_user()
        user2 = create_user(email='em@ail.com')
        offerer = create_offerer(siren='123456789')
        venue1 = create_venue(offerer, postal_code='37160')
        venue2 = create_venue(offerer, postal_code='37160', siret=offerer.siren + '63732')
        user_offerer1 = create_user_offerer(user1, offerer)
        user_offerer2 = create_user_offerer(user2, offerer)
        repository.save(user_offerer1, user_offerer2, venue1, venue2)

        # When
        number_of_offerers = count_offerer_by_departement('37')

        # Then
        assert number_of_offerers == 1


class CountOffererWithStockTest:
    def test_return_zero_if_no_offerer(self, app):
        # When
        number_of_offerers = count_offerer_with_stock()

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_return_1_if_offerer_with_user_offerer_and_stock(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer)
        repository.save(user_offerer, stock)

        # When
        number_of_offerers = count_offerer_with_stock()

        # Then
        assert number_of_offerers == 1

    @clean_database
    def test_return_0_if_offerer_without_user_offerer(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer)
        repository.save(offerer, stock)

        # When
        number_of_offerers = count_offerer_with_stock()

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_return_0_if_offerer_without_stock(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        user_offerer = create_user_offerer(user, offerer)

        repository.save(user_offerer)

        # When
        number_of_offerers = count_offerer_with_stock()

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_return_1_if_offerer_with_user_offerer_and_two_stock(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer)
        stock2 = create_stock(offer=offer)
        repository.save(user_offerer, stock1, stock2)

        # When
        number_of_offerers = count_offerer_with_stock()

        # Then
        assert number_of_offerers == 1

    @clean_database
    def test_return_1_if_offerer_with_2_user_offerers_and_stock(self, app):
        # Given
        user1 = create_user()
        user2 = create_user(email='other@email.com')
        offerer = create_offerer()
        user_offerer1 = create_user_offerer(user1, offerer)
        user_offerer2 = create_user_offerer(user2, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer)
        stock2 = create_stock(offer=offer)
        repository.save(user_offerer1, user_offerer2, stock1, stock2)

        # When
        number_of_offerers = count_offerer_with_stock()

        # Then
        assert number_of_offerers == 1

    @clean_database
    def test_returns_0_when_only_offerers_with_activation_offers(self, app):
        # Given
        user = create_user(email='first@example.net')
        offerer = create_offerer(siren='111111111')
        create_user_offerer(user, offerer)
        venue = create_venue(offerer, siret='1111111110001', postal_code='75018')
        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        offer2 = create_offer_with_event_product(venue, event_type=ThingType.ACTIVATION)
        stock1 = create_stock(offer=offer1)
        stock2 = create_stock(offer=offer2)

        repository.save(stock1, stock2)

        # When
        number_of_offerers = count_offerer_with_stock()

        # Then
        assert number_of_offerers == 0


class CountOffererWithStockByDepartementTest:
    def test_return_zero_if_no_offerer(self, app):
        # When
        number_of_offerers = count_offerer_with_stock_by_departement('76')

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_return_0_if_offerer_without_user_offerer(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='76214')
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer)
        repository.save(offerer, stock)

        # When
        number_of_offerers = count_offerer_with_stock_by_departement('76')

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_return_0_if_offerer_without_stock(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='76214')
        user = create_user()
        user_offerer = create_user_offerer(user, offerer)

        repository.save(user_offerer, venue)

        # When
        number_of_offerers = count_offerer_with_stock_by_departement('76')

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_return_1_if_offerer_with_user_offerer_and_two_stock(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, postal_code='76130')
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer)
        stock2 = create_stock(offer=offer)
        repository.save(user_offerer, stock1, stock2)

        # When
        number_of_offerers = count_offerer_with_stock_by_departement('76')

        # Then
        assert number_of_offerers == 1

    @clean_database
    def test_counts_offerer_only_once_even_if_it_has_multiple_user_offerers_and_stock_in_departement(self, app):
        # Given
        user1 = create_user()
        user2 = create_user(email='associate@email.com')
        offerer = create_offerer()
        user_offerer1 = create_user_offerer(user1, offerer)
        user_offerer2 = create_user_offerer(user2, offerer)
        venue = create_venue(offerer, postal_code='76130')
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer)
        stock2 = create_stock(offer=offer)
        repository.save(user_offerer1, user_offerer2, stock1, stock2)

        # When
        number_of_offerers = count_offerer_with_stock_by_departement('76')

        # Then
        assert number_of_offerers == 1

    @clean_database
    def test_return_1_when_filtered_by_departement(self, app):
        # Given
        first_user = create_user(email='first@example.net')
        first_offerer = create_offerer(siren='111111111')
        first_user_offerer = create_user_offerer(first_user, first_offerer)
        first_venue = create_venue(first_offerer, siret='1111111110001', postal_code='75018')
        first_offer = create_offer_with_thing_product(first_venue)
        first_stock = create_stock(offer=first_offer)

        second_user = create_user(email='second@example.net')
        second_offerer = create_offerer(siren='222222222')
        second_user_offerer = create_user_offerer(second_user, second_offerer)
        second_venue = create_venue(second_offerer, siret='2222222220001', postal_code='76230')
        second_offer = create_offer_with_thing_product(second_venue)
        second_stock = create_stock(offer=second_offer)

        repository.save(first_stock, first_user_offerer, second_stock, second_user_offerer)

        # When
        number_of_offerers = count_offerer_with_stock_by_departement('76')

        # Then
        assert number_of_offerers == 1

    @clean_database
    def test_return_0_when_filtered_by_departement_and_none_is_found(self, app):
        # Given
        first_user = create_user(email='first@example.net')
        first_offerer = create_offerer(siren='111111111')
        first_user_offerer = create_user_offerer(first_user, first_offerer)
        first_venue = create_venue(first_offerer, siret='1111111110001', postal_code='75018')
        first_offer = create_offer_with_thing_product(first_venue)
        first_stock = create_stock(offer=first_offer)

        second_user = create_user(email='second@example.net')
        second_offerer = create_offerer(siren='222222222')
        second_user_offerer = create_user_offerer(second_user, second_offerer)
        second_venue = create_venue(second_offerer, siret='2222222220001', postal_code='76230')
        second_offer = create_offer_with_thing_product(second_venue)
        second_stock = create_stock(offer=second_offer)

        repository.save(first_stock, first_user_offerer, second_stock, second_user_offerer)

        # When
        number_of_offerers = count_offerer_with_stock_by_departement('42')

        # Then
        assert number_of_offerers == 0

    @clean_database
    def test_returns_0_when_only_offerers_with_activation_offers(self, app):
        # Given
        user = create_user(email='first@example.net')
        offerer = create_offerer(siren='111111111')
        create_user_offerer(user, offerer)
        venue = create_venue(offerer, siret='1111111110001', postal_code='76018')
        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        offer2 = create_offer_with_event_product(venue, event_type=ThingType.ACTIVATION)
        stock1 = create_stock(offer=offer1)
        stock2 = create_stock(offer=offer2)

        repository.save(stock1, stock2)

        # When
        number_of_offerers = count_offerer_with_stock_by_departement('76')

        # Then
        assert number_of_offerers == 0


@clean_database
def test_find_all_emails_of_user_offerers_admins_returns_list_of_user_emails_having_user_offerer_with_admin_rights_on_offerer(
        app):
    # Given
    offerer = create_offerer()
    user_admin1 = create_user(email='admin1@offerer.com')
    user_admin2 = create_user(email='admin2@offerer.com')
    user_editor = create_user(email='editor@offerer.com')
    user_admin_not_validated = create_user(email='admin_not_validated@offerer.com')
    user_random = create_user(email='random@user.com')
    user_offerer_admin1 = create_user_offerer(user_admin1, offerer, is_admin=True)
    user_offerer_admin2 = create_user_offerer(user_admin2, offerer, is_admin=True)
    user_offerer_admin_not_validated = create_user_offerer(user_admin_not_validated, offerer,
                                                           validation_token=secrets.token_urlsafe(20), is_admin=True)
    user_offerer_editor = create_user_offerer(user_editor, offerer, is_admin=False)
    repository.save(user_random, user_offerer_admin1, user_offerer_admin2, user_offerer_admin_not_validated,
                  user_offerer_editor)

    # When
    emails = find_all_emails_of_user_offerers_admins(offerer.id)

    # Then
    assert set(emails) == {'admin1@offerer.com', 'admin2@offerer.com'}
    assert type(emails) == list


@clean_database
def test_find_email_of_user_offerer_should_returns_email(
        app):
    # Given
    offerer = create_offerer()
    pro_user = create_user(email='pro@example.com')
    user_offerer = create_user_offerer(pro_user, offerer)

    repository.save(pro_user, user_offerer)

    # When
    result = find_new_offerer_user_email(offerer.id)

    # Then
    assert result == 'pro@example.com'


@clean_database
def test_find_first_by_user_offerer_id_returns_the_first_offerer_that_was_created(app):
    # given
    user = create_user()
    offerer1 = create_offerer(name='offerer1', siren='123456789')
    offerer2 = create_offerer(name='offerer2', siren='789456123')
    offerer3 = create_offerer(name='offerer2', siren='987654321')
    user_offerer1 = create_user_offerer(user, offerer1)
    user_offerer2 = create_user_offerer(user, offerer2)
    repository.save(user_offerer1, user_offerer2, offerer3)

    # when
    offerer = find_first_by_user_offerer_id(user_offerer1.id)

    # then
    assert offerer.id == offerer1.id
