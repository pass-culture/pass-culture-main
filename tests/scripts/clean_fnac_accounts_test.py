import pytest

from models import PcObject, UserOfferer, Offer, Venue, RightsType
from scripts.clean_fnac_accounts import find_all_fnac_users, find_all_OK_fnac_offerers, \
    create_all_possible_user_offerers, \
    clear_all_existing_user_offerers, move_offers_from_one_venue_to_another, delete_all_physical_managed_venues
from tests.conftest import clean_database
from tests.test_utils import create_user, create_offerer, create_user_offerer, create_venue, \
    create_offer_with_thing_product, create_offer_with_event_product

ALL_OK_FNAC_SIREN = ['350127460', '434001954', '334473352', '343282380']


@pytest.mark.standalone
class FindAllOKFnacUsersTest:
    @clean_database
    def test_retrieves_users_with_email_ending_with_fnac_dot_com_and_fnacdarty_dot_com_only(self, app):
        # Given
        user_fnac = create_user(email='toto@fnac.com')
        user_fnacdarty = create_user(email='toto@fnacdarty.com')
        user_not_fnac = create_user(email='toto@cultura.com')

        PcObject.check_and_save(user_fnac, user_fnacdarty, user_not_fnac)

        # When
        users = find_all_fnac_users()

        # Then
        assert len(users) == 2
        assert user_not_fnac not in users


@pytest.mark.standalone
class FindAllFnacStructuresTest:
    @clean_database
    def test_only_retrieves_offerers_with_fnac_siren(self, app):
        # Given
        fnac_offerers = [create_offerer(siren=siren) for siren in ALL_OK_FNAC_SIREN]
        other_offerer = create_offerer(siren='123456789')
        PcObject.check_and_save(*(fnac_offerers + [other_offerer]))

        # When
        offerers = find_all_OK_fnac_offerers()

        # Then
        assert len(offerers) == 4
        assert other_offerer not in offerers


@pytest.mark.standalone
class CreateAllPossibleUserOfferersTest:
    @clean_database
    def test_should_create_user_offerers_linking_all_fnac_users_and_offerers_only_if_they_do_not_exist(self, app):
        # Given
        users = [create_user(email=f'{i}@toto.com') for i in range(2)]
        offerers = [create_offerer(siren=f'12345678{i}') for i in range(3)]
        user_offerer = create_user_offerer(users[0], offerers[0])
        PcObject.check_and_save(user_offerer)

        # When
        create_all_possible_user_offerers(users, offerers)

        # Then
        user_offerers = UserOfferer.query.all()
        assert len(user_offerers) == 6
        for user_offerer in user_offerers:
            assert user_offerer.user in users
            assert user_offerer.offerer in offerers
            assert user_offerer.rights == RightsType.editor


@pytest.mark.standalone
class ClearAllExistingUserOfferersTest:
    @clean_database
    def test_should_only_delete_user_offerers_linked_to_given_offerer(self, app):
        # Given
        offerer = create_offerer('123456789')
        other_offerer = create_offerer('987654321')

        user1 = create_user(email='1@email.com')
        user2 = create_user(email='2@email.com')

        user_offerer1 = create_user_offerer(user1, offerer)
        user_offerer2 = create_user_offerer(user2, offerer)
        other_user_offerer = create_user_offerer(user2, other_offerer)

        PcObject.check_and_save(user_offerer1, user_offerer2, other_user_offerer)

        # When
        clear_all_existing_user_offerers(offerer.id)

        # Then
        user_offerers = UserOfferer.query.all()
        assert len(user_offerers) == 1
        assert user_offerers[0].offerer.siren != '123456789'


@pytest.mark.standalone
class MoveOffersFromOneVenueToAnotherTest:
    @clean_database
    def test_unlinks_offers_from_origin_venue_and_links_it_to_target(self, app):
        # Given
        origin_offerer = create_offerer(siren='123456789')
        target_offerer = create_offerer(siren='987654321')
        other_offerer = create_offerer(siren='123456788')

        origin_venue = create_venue(origin_offerer, siret=origin_offerer.siren + '12345')
        target_venue = create_venue(target_offerer, siret=target_offerer.siren + '12345')
        other_venue = create_venue(other_offerer, siret=other_offerer.siren + '12345')

        origin_offer1 = create_offer_with_thing_product(origin_venue)
        origin_offer2 = create_offer_with_event_product(origin_venue)
        other_offer = create_offer_with_event_product(other_venue)
        PcObject.check_and_save(origin_offer1, origin_offer2, target_venue, other_offer)

        # When
        move_offers_from_one_venue_to_another(origin_venue.id, target_venue.id)

        # Then
        assert Offer.query.join(Venue).filter_by(id=target_venue.id).count() == 2
        assert Offer.query.join(Venue).filter_by(id=origin_venue.id).count() == 0

    @clean_database
    def test_should_not_raise_error_when_no_offers_linked_to_venue(self, app):
        # Given
        origin_offerer = create_offerer(siren='123456789')
        target_offerer = create_offerer(siren='987654321')

        origin_venue = create_venue(origin_offerer, siret=origin_offerer.siren + '12345')
        target_venue = create_venue(target_offerer, siret=target_offerer.siren + '12345')
        PcObject.check_and_save(origin_venue, target_venue)

        try:
            # When
            move_offers_from_one_venue_to_another(origin_venue.id, target_venue.id)
        # Then
        except ValueError:
            assert False


@pytest.mark.standalone
class DeleteAllPhysicalManagedVenuesTest:
    @clean_database
    def test_removes_all_physical_venues(self, app):
        # Given
        offerer = create_offerer()
        other_offerer = create_offerer(siren='987654321')
        venue1 = create_venue(offerer, siret=offerer.siren + '00001', is_virtual=False)
        venue2 = create_venue(offerer, siret=offerer.siren + '00002', is_virtual=False)
        other_venue = create_venue(other_offerer, siret=other_offerer.siren + '00001', is_virtual=False)

        PcObject.check_and_save(venue1, venue2, other_venue)

        # When
        delete_all_physical_managed_venues(offerer.id)

        # Then
        venues = Venue.query.all()
        assert len(venues) == 1
        assert venues[0].managingOfferer.siren == '987654321'

    @clean_database
    def test_keeps_virtual_venues(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, siret=None, is_virtual=True)

        PcObject.check_and_save(venue)

        # When
        delete_all_physical_managed_venues(offerer.id)

        # Then
        venues = Venue.query.all()
        assert len(venues) == 1
