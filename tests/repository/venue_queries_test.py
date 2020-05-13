""" repository venue queries """
from datetime import datetime, timedelta
import pytest
from sqlalchemy.orm.exc import MultipleResultsFound

from repository import repository
from repository.venue_queries import find_by_managing_user, \
    find_venue_without_siret_by_managing_offerer_id_and_name, find_by_managing_offerer_id_and_siret
from tests.conftest import clean_database
from tests.model_creators.activity_creators import create_venue_activity, save_all_activities
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_user_offerer
from tests.model_creators.specific_creators import create_stock_from_event_occurrence, create_stock_with_thing_offer, \
    create_offer_with_thing_product, create_offer_with_event_product, create_event_occurrence


class FindVenuesByManagingUserTest:
    @clean_database
    def test_returns_venues_that_a_user_manages(self):
        # given
        user = create_user(email='user@example.net')

        managed_offerer = create_offerer(
            name='Shakespear company', siren='987654321')
        managed_user_offerer = create_user_offerer(user, managed_offerer)
        managed_venue = create_venue(
            managed_offerer, name='National Shakespear Theater', siret='98765432112345')

        non_managed_offerer = create_offerer(
            name='Bookshop', siren='123456789')
        other_user = create_user(email='bookshop.pro@example.net')
        non_managed_user_offerer = create_user_offerer(
            other_user, non_managed_offerer)
        non_managed_venue = create_venue(
            non_managed_offerer, name='Contes et légendes', siret='12345678912345')

        repository.save(managed_user_offerer, managed_venue,
                        non_managed_user_offerer, non_managed_venue)

        # when
        venues = find_by_managing_user(user)

        # then
        assert len(venues) == 1
        assert venues[0] == managed_venue


class FindByManagingOffererIdAndNameForVenueWithoutSiretTest:
    @clean_database
    def test_return_none_when_offerer_does_not_have_any_matching_venue_name(self):
        # Given
        offerer = create_offerer()
        not_matching_venue = create_venue(
            offerer, name='Not matching name', siret=None, comment='comment')
        repository.save(not_matching_venue)

        # When
        venue = find_venue_without_siret_by_managing_offerer_id_and_name(
            offerer.id, 'searched name')

        # Then
        assert len(venue) == 0

    @clean_database
    def test_does_not_match_venues_with_a_wrong_attribute(self):
        # Given
        offerer = create_offerer()
        wrong_offerer = create_offerer(siren='123456798')
        matching_venue = create_venue(
            offerer, name='Matching name', siret=None, comment='comment')
        not_matching_venue1 = create_venue(
            offerer, name='Not matching name', siret=None, comment='comment')
        not_matching_venue2 = create_venue(offerer, name='Matching name')
        not_matching_venue3 = create_venue(
            wrong_offerer, name='Matching name', siret=None, comment='comment')
        repository.save(matching_venue, not_matching_venue1,
                        not_matching_venue2, not_matching_venue3)

        # When
        venues = find_venue_without_siret_by_managing_offerer_id_and_name(
            offerer.id, 'Matching name')

        # Then
        assert len(venues) == 1
        venue = venues[0]
        assert venue.id == matching_venue.id
        assert venue.siret is None
        assert venue.managingOffererId == offerer.id


class FindByManagingOffererIdAndSiretTest:
    @clean_database
    def test_return_none_when_not_matching_venues(self):
        # Given
        offerer = create_offerer()
        not_matching_venue = create_venue(offerer, siret='12345678988888')
        repository.save(not_matching_venue)

        # When
        venue = find_by_managing_offerer_id_and_siret(
            offerer.id, '12345678912345')

        # Then
        assert venue is None

    @clean_database
    def test_return_matching_venue(self):
        # Given
        offerer = create_offerer()
        matching_venue = create_venue(offerer, siret='12345678912345')
        repository.save(matching_venue)

        # When
        venue = find_by_managing_offerer_id_and_siret(
            offerer.id, '12345678912345')

        # Then
        assert venue.id == matching_venue.id
        assert venue.siret == '12345678912345'
        assert venue.managingOffererId == offerer.id
