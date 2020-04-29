import pytest
from tests.model_creators.generic_creators import (create_offerer,
                                                   create_venue)
from domain.bank_information import check_offerer_presence, check_venue_presence, check_venue_queried_by_name, VenueMatchingError, new_application_can_update_bank_information
from tests.model_creators.generic_creators import create_bank_information
from models.bank_information import BankInformationStatus


class NewApplicationCanUpdateBankInformationTest():
    def test_returns_true_if_same_application_id(self):
        # given
        bank_information = create_bank_information(application_id=3)

        # when
        can_update_witness = new_application_can_update_bank_information(
            bank_information, 4, BankInformationStatus.DRAFT)
        can_update = new_application_can_update_bank_information(
            bank_information, 3, BankInformationStatus.DRAFT)

        # then
        assert not can_update_witness
        assert can_update

    def test_always_returns_true_if_application_is_validated(self):
        # given
        bank_information1 = create_bank_information()
        bank_information2 = create_bank_information(
            status=BankInformationStatus.DRAFT, bic="", iban="")
        bank_information3 = create_bank_information(
            status=BankInformationStatus.REJECTED, bic="", iban="")

        # when
        can_update_witness = new_application_can_update_bank_information(
            bank_information1, 4, BankInformationStatus.DRAFT)
        can_update1 = new_application_can_update_bank_information(
            bank_information1, 4, BankInformationStatus.ACCEPTED)
        can_update2 = new_application_can_update_bank_information(
            bank_information2, 4, BankInformationStatus.ACCEPTED)
        can_update3 = new_application_can_update_bank_information(
            bank_information3, 4, BankInformationStatus.ACCEPTED)

        # then
        assert not can_update_witness
        assert can_update1
        assert can_update2
        assert can_update3

    def test_doesnt_returns_trus_if_previous_application_was_valready_validated(self):
        # given
        bank_information = create_bank_information()

        # when
        can_update1 = new_application_can_update_bank_information(
            bank_information, 4, BankInformationStatus.ACCEPTED)
        can_update2 = new_application_can_update_bank_information(
            bank_information, 4, BankInformationStatus.REJECTED)
        can_update3 = new_application_can_update_bank_information(
            bank_information, 4, BankInformationStatus.DRAFT)

        # then
        assert can_update1
        assert not can_update2
        assert not can_update3


class CheckOffererPresenceTest:
    def test_raises_an_error_if_no_offerer_found(self):
        # given
        offerer = None

        # when
        with pytest.raises(VenueMatchingError) as error:
            check_offerer_presence(offerer)

        # then
        assert error.value.args == ("Offerer not found",)


class CheckVenuePresenceTest:
    def test_raises_an_error_if_no_venue_found(self):
        # given
        venue = None

        # when
        with pytest.raises(VenueMatchingError) as error:
            check_venue_presence(venue)

        # then
        assert error.value.args == ("Venue not found",)


class CheckVenueQueriedByNameTest:
    def test_raises_an_error_if_no_venue_found(self):
        # given
        venues = []

        # when
        with pytest.raises(VenueMatchingError) as error:
            check_venue_queried_by_name(venues)

        # then
        assert error.value.args == ("Venue name for found",)

    def test_raise_an_error_if_more_than_one_venue_found(self):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        venue1 = create_venue(offerer=offerer)
        venues = [venue, venue1]

        # when
        with pytest.raises(VenueMatchingError) as error:
            check_venue_queried_by_name(venues)

        # then
        assert error.value.args == ("Multiple venues found",)
