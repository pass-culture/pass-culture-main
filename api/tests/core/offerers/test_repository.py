from datetime import datetime
from datetime import timedelta

import pytest

import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
from pcapi.core.offerers import exceptions
from pcapi.core.offerers import models
from pcapi.core.offerers import repository
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.core.users import factories as users_factories
from pcapi.models.offer_mixin import OfferStatus


pytestmark = pytest.mark.usefixtures("db_session")


class GetAllVenueLabelsTest:
    def test_get_all_venue_labels(self):
        label1 = offerers_factories.VenueLabelFactory()
        label2 = offerers_factories.VenueLabelFactory()

        assert set(repository.get_all_venue_labels()) == {label1, label2}


class GetAllOfferersForUserTest:
    def should_return_all_offerers_for_an_admin(self) -> None:
        # Given
        admin = users_factories.AdminFactory()
        offerer = offerers_factories.OffererFactory()

        # When
        offerers = repository.get_all_offerers_for_user(user=admin).all()

        # Then
        assert len(offerers) == 1
        assert offerers[0].id == offerer.id

    def should_return_pro_offerers_only(self) -> None:
        # Given
        pro = users_factories.ProFactory()
        pro_offerer_attachment = offerers_factories.UserOffererFactory(user=pro)
        other_offerer = offerers_factories.OffererFactory()

        # When
        offerers = repository.get_all_offerers_for_user(user=pro).all()

        # Then
        assert len(offerers) == 1
        offerers_ids = [offerer.id for offerer in offerers]
        assert pro_offerer_attachment.offerer.id in offerers_ids
        assert other_offerer.id not in offerers_ids

    def should_return_non_validated_offerers(self) -> None:
        # Given
        pro = users_factories.ProFactory()
        pro_offerer_attachment = offerers_factories.UserNotValidatedOffererFactory(user=pro)

        # When
        offerers = repository.get_all_offerers_for_user(user=pro).all()

        # Then
        assert len(offerers) == 1
        offerers_ids = [offerer.id for offerer in offerers]
        assert pro_offerer_attachment.offerer.id in offerers_ids

    def should_not_return_offerers_with_non_validated_attachment_to_given_pro(self) -> None:
        pro = users_factories.ProFactory()
        offerers_factories.NotValidatedUserOffererFactory(user=pro)
        assert repository.get_all_offerers_for_user(user=pro).all() == []

    def should_not_return_deactivated_offerers(self) -> None:
        # Given
        admin = users_factories.AdminFactory()
        offerers_factories.OffererFactory(isActive=False)

        # When
        offerers = repository.get_all_offerers_for_user(user=admin).all()

        # Then
        assert len(offerers) == 0

    def test_search_keywords_in_offerer_name(self):
        offerer1 = offerers_factories.OffererFactory(name="cinéma")
        offerer2 = offerers_factories.OffererFactory(name="théâtre")
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer1)
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer2)

        offerers = repository.get_all_offerers_for_user(user=pro, keywords="cinema").all()

        assert len(offerers) == 1
        assert offerers == [offerer1]

    def test_search_keywords_in_venue_name(self):
        offerer1 = offerers_factories.OffererFactory(name="dummy")
        offerers_factories.VenueFactory(managingOfferer=offerer1, name="cinéma")
        offerer2 = offerers_factories.OffererFactory(name="dummy")
        offerers_factories.VenueFactory(managingOfferer=offerer2, name="théâtre")
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer1)
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer2)

        offerers = repository.get_all_offerers_for_user(user=pro, keywords="cinema").all()

        assert len(offerers) == 1
        assert offerers == [offerer1]

    class WithValidatedFilterTest:
        def should_return_all_pro_offerers_when_filter_is_none(self) -> None:
            # Given
            pro = users_factories.ProFactory()
            pro_attachment_to_validated_offerer = offerers_factories.UserOffererFactory(user=pro)
            pro_attachment_to_unvalidated_offerer = offerers_factories.UserNotValidatedOffererFactory(user=pro)

            # When
            offerers = repository.get_all_offerers_for_user(user=pro).all()

            # Then
            assert len(offerers) == 2
            offerers_ids = [offerer.id for offerer in offerers]
            assert pro_attachment_to_validated_offerer.offerer.id in offerers_ids
            assert pro_attachment_to_unvalidated_offerer.offerer.id in offerers_ids

        def should_return_only_validated_offerers_when_filter_is_true(self) -> None:
            # Given
            pro = users_factories.ProFactory()
            pro_attachment_to_validated_offerer = offerers_factories.UserOffererFactory(user=pro)
            pro_attachment_to_unvalidated_offerer = offerers_factories.UserNotValidatedOffererFactory(user=pro)

            # When
            offerers = repository.get_all_offerers_for_user(user=pro, validated=True).all()

            # Then
            assert len(offerers) == 1
            offerers_ids = [offerer.id for offerer in offerers]
            assert pro_attachment_to_validated_offerer.offerer.id in offerers_ids
            assert pro_attachment_to_unvalidated_offerer.offerer.id not in offerers_ids

        def should_return_only_unvalidated_offerers_when_filter_is_false(self) -> None:
            # Given
            pro = users_factories.ProFactory()
            pro_attachment_to_validated_offerer = offerers_factories.UserOffererFactory(user=pro)
            pro_attachment_to_unvalidated_offerer = offerers_factories.UserNotValidatedOffererFactory(user=pro)

            # When
            offerers = repository.get_all_offerers_for_user(user=pro, validated=False).all()

            # Then
            assert len(offerers) == 1
            offerers_ids = [offerer.id for offerer in offerers]
            assert pro_attachment_to_validated_offerer.offerer.id not in offerers_ids
            assert pro_attachment_to_unvalidated_offerer.offerer.id in offerers_ids


class FindUserOffererByValidationTokenTest:
    def test_return_user_offerer_given_validation_token(self):
        # Given
        user_offerer_expected = offerers_factories.NotValidatedUserOffererFactory()

        # When
        user_offerer_received = repository.find_user_offerer_by_validation_token(user_offerer_expected.validationToken)

        # Then
        assert user_offerer_received.id == user_offerer_expected.id

    def test_return_nothing_when_validation_token_does_not_exist(self):
        # Given
        offerers_factories.NotValidatedUserOffererFactory()

        # When
        user_offerer_received = repository.find_user_offerer_by_validation_token("ANOTHER TOKEN")

        # Then
        assert user_offerer_received is None


class FindOffererByValidationTokenTest:
    def test_return_offerer_given_validation_token(self):
        # Given
        user_offerer_expected = offerers_factories.UserNotValidatedOffererFactory()

        # When
        offerer_received = repository.find_offerer_by_validation_token(user_offerer_expected.offerer.validationToken)

        # Then
        assert offerer_received.id == user_offerer_expected.offerer.id

    def test_return_nothing_when_validation_token_does_not_exist(self):
        # Given
        offerers_factories.UserNotValidatedOffererFactory()

        # When
        offerer_received = repository.find_offerer_by_validation_token("ANOTHER TOKEN")

        # Then
        assert offerer_received is None


class FindNewOffererUserEmailTest:
    def test_find_existing_email(self):
        offerer = offerers_factories.OffererFactory()
        pro_user = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(offerer=offerer, user=pro_user)

        result = repository.find_new_offerer_user_email(offerer.id)

        assert result == pro_user.email

    def test_find_unknown_email(self):
        with pytest.raises(exceptions.CannotFindOffererUserEmail):
            repository.find_new_offerer_user_email(offerer_id=1)


class FilterOfferersWithKeywordsStringTest:
    def test_find_filtered_offerers_with_keywords(self):
        offerer_with_only_virtual_venue_with_offer = offerers_factories.OffererFactory(siren="123456785")
        offerer_with_both_venues_offer_on_both = offerers_factories.OffererFactory(siren="123456782")
        offerer_with_both_venues_offer_on_virtual = offerers_factories.OffererFactory(siren="123456783")
        offerer_with_both_venues_offer_on_not_virtual = offerers_factories.OffererFactory(siren="123456784")

        virtual_venue_with_offer_1 = offerers_factories.VenueFactory(
            managingOfferer=offerer_with_only_virtual_venue_with_offer, isVirtual=True, siret=None
        )
        virtual_venue_with_offer_3 = offerers_factories.VenueFactory(
            managingOfferer=offerer_with_both_venues_offer_on_both,
            isVirtual=True,
            siret=None,
            publicName="Librairie des mots perdus",
        )
        venue_with_offer_3 = offerers_factories.VenueFactory(
            managingOfferer=offerer_with_both_venues_offer_on_both,
            siret="12345678212345",
            publicName="Librairie des mots perdus",
        )
        virtual_venue_with_offer_4 = offerers_factories.VenueFactory(
            managingOfferer=offerer_with_both_venues_offer_on_virtual,
            isVirtual=True,
            siret=None,
            publicName="Librairie des mots perdus",
        )
        venue_with_offer_5 = offerers_factories.VenueFactory(
            managingOfferer=offerer_with_both_venues_offer_on_not_virtual,
            siret="12345678412345",
            publicName="Librairie des mots perdus",
        )
        offerers_factories.VenueFactory(publicName="something else")

        offers_factories.ThingOfferFactory(venue=virtual_venue_with_offer_1, url="http://url.com")
        offers_factories.ThingOfferFactory(venue=virtual_venue_with_offer_3, url="http://url.com")
        offers_factories.ThingOfferFactory(venue=virtual_venue_with_offer_4, url="http://url.com")
        offers_factories.EventOfferFactory(venue=venue_with_offer_3)
        offers_factories.EventOfferFactory(venue=venue_with_offer_5)

        one_keyword_search = repository.filter_offerers_with_keywords_string(
            models.Offerer.query.join(models.Venue), "perdus"
        )
        partial_keyword_search = repository.filter_offerers_with_keywords_string(
            models.Offerer.query.join(models.Venue), "Libr"
        )
        two_keywords_search = repository.filter_offerers_with_keywords_string(
            models.Offerer.query.join(models.Venue), "Librairie perd"
        )
        two_partial_keywords_search = repository.filter_offerers_with_keywords_string(
            models.Offerer.query.join(models.Venue), "Lib perd"
        )

        assert {
            offerer_with_both_venues_offer_on_both,
            offerer_with_both_venues_offer_on_virtual,
            offerer_with_both_venues_offer_on_not_virtual,
        } == set(one_keyword_search)
        assert {
            offerer_with_both_venues_offer_on_both,
            offerer_with_both_venues_offer_on_virtual,
            offerer_with_both_venues_offer_on_not_virtual,
        } == set(partial_keyword_search)
        assert {
            offerer_with_both_venues_offer_on_both,
            offerer_with_both_venues_offer_on_virtual,
            offerer_with_both_venues_offer_on_not_virtual,
        } == set(two_keywords_search)
        assert {
            offerer_with_both_venues_offer_on_both,
            offerer_with_both_venues_offer_on_virtual,
            offerer_with_both_venues_offer_on_not_virtual,
        } == set(two_partial_keywords_search)


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
    base_query = offers_models.Offer.query.join(models.Venue).join(models.Offerer)
    offers = repository.filter_query_where_user_is_user_offerer_and_is_validated(base_query, pro).all()

    # Then
    assert offer1 in offers
    assert offer2 in offers
    assert offer3 not in offers


class HasVenueWithoutDraftOrAcceptedBankInformationTest:
    def test_venue_with_accepted_bank_information(self):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        finance_factories.BankInformationFactory(venue=venue, status=finance_models.BankInformationStatus.ACCEPTED)

        assert not repository.has_physical_venue_without_draft_or_accepted_bank_information(offerer_id=offerer.id)

    def test_venue_with_draft_bank_information(self):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        finance_factories.BankInformationFactory(venue=venue, status=finance_models.BankInformationStatus.DRAFT)

        assert not repository.has_physical_venue_without_draft_or_accepted_bank_information(offerer_id=offerer.id)

    def test_venues_with_rejected_and_accepted_bank_information(self):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
        venue_with_rejected_bank_information = offerers_factories.VenueFactory(managingOfferer=offerer)
        finance_factories.BankInformationFactory(
            venue=venue_with_rejected_bank_information, status=finance_models.BankInformationStatus.REJECTED
        )
        venue_with_rejected_bank_information = offerers_factories.VenueFactory(managingOfferer=offerer)
        finance_factories.BankInformationFactory(
            venue=venue_with_rejected_bank_information, status=finance_models.BankInformationStatus.ACCEPTED
        )

        assert repository.has_physical_venue_without_draft_or_accepted_bank_information(offerer_id=offerer.id)

    def test_venues_with_missing_and_accepted_bank_information(self):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_with_rejected_bank_information = offerers_factories.VenueFactory(managingOfferer=offerer)
        finance_factories.BankInformationFactory(
            venue=venue_with_rejected_bank_information, status=finance_models.BankInformationStatus.ACCEPTED
        )

        assert repository.has_physical_venue_without_draft_or_accepted_bank_information(offerer_id=offerer.id)


class HasDigitalVenueWithAtLeastOneOfferTest:
    def test_digital_venue_with_offer(self):
        offerer = offerers_factories.OffererFactory()
        digital_venue = offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
        offers_factories.DigitalOfferFactory(venue=digital_venue)

        assert repository.has_digital_venue_with_at_least_one_offer(offerer.id)

    def test_digital_venue_without_offer(self):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer)

        assert not repository.has_digital_venue_with_at_least_one_offer(offerer.id)

    def test_digital_venue_with_draft_offer(self):
        offerer = offerers_factories.OffererFactory()
        digital_venue = offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
        offers_factories.DigitalOfferFactory(venue=digital_venue, validation=OfferStatus.DRAFT.name)

        assert not repository.has_digital_venue_with_at_least_one_offer(offerer.id)


class GetSirenByOffererIdTest:
    def test_return_siren_for_offerer_id(self):
        offerer = offerers_factories.OffererFactory()

        assert repository.find_siren_by_offerer_id(offerer.id) == offerer.siren

    def test_return_error_when_no_siren_found(self):
        with pytest.raises(exceptions.CannotFindOffererSiren):
            repository.find_siren_by_offerer_id(0)


class GetOfferersValidatedThreeDaysAgoWithNoVenuesCreatedTest:
    def test_return_offerer_validated_three_days_ago_with_no_physical_venue_and_digital_venue_with_no_offers(
        self,
    ):
        # given
        five_days_ago = datetime.utcnow() - timedelta(days=5)
        offerer_with_venue = offerers_factories.OffererFactory(dateValidated=five_days_ago)
        offerers_factories.VenueFactory(managingOfferer=offerer_with_venue)

        three_days_ago = datetime.utcnow() - timedelta(days=3)
        offerer_with_venue2 = offerers_factories.OffererFactory(dateValidated=three_days_ago)
        offerers_factories.VenueFactory(managingOfferer=offerer_with_venue2)

        offerer_with_digital_venue_and_has_offers = offerers_factories.OffererFactory(dateValidated=three_days_ago)
        digital_venue = offerers_factories.VirtualVenueFactory(
            managingOfferer=offerer_with_digital_venue_and_has_offers
        )
        offers_factories.DigitalOfferFactory(venue=digital_venue)

        offerer_with_only_digital_venue_and_no_offers = offerers_factories.OffererFactory(dateValidated=three_days_ago)
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer_with_only_digital_venue_and_no_offers)

        # when
        offerers = repository.find_offerers_validated_3_days_ago_with_no_venues()

        # then
        assert len(offerers) == 1
        assert offerers[0] == offerer_with_only_digital_venue_and_no_offers


class HasNoOfferAndAtLeastOnePhysicalVenueAndCreatedSinceXDaysTest:
    def test_should_return_two_venues_of_offerer_without_offers_and_validated_5_days_ago(self):
        five_days_ago = datetime.utcnow() - timedelta(days=5)
        # Offerer with two physical venues and one offer => venues should not be returned
        offerer_with_two_venues = offerers_factories.OffererFactory(dateValidated=five_days_ago)
        venue_with_offers = offerers_factories.VenueFactory(managingOfferer=offerer_with_two_venues)
        offerers_factories.VenueFactory(managingOfferer=offerer_with_two_venues)
        offers_factories.OfferFactory(venue=venue_with_offers)

        # Offerer with only virtual venue and no offer => venue should not be returned
        offerer_with_only_virtual_venue = offerers_factories.OffererFactory(dateValidated=five_days_ago)
        offerers_factories.VenueFactory(managingOfferer=offerer_with_only_virtual_venue, isVirtual=True, siret=None)

        # Offerer with two physical venues and no offer => venus should be returned
        offerer_with_physical_venue = offerers_factories.OffererFactory(dateValidated=five_days_ago)
        venue_without_offer_1 = offerers_factories.VenueFactory(managingOfferer=offerer_with_physical_venue)
        venue_without_offer_2 = offerers_factories.VenueFactory(managingOfferer=offerer_with_physical_venue)

        # Offerer with virtual venue and one offer => venue should not be returned
        offerer_with_virtual_offer = offerers_factories.OffererFactory(dateValidated=five_days_ago)
        virtual_venue = offerers_factories.VenueFactory(
            managingOfferer=offerer_with_virtual_offer, isVirtual=True, siret=None
        )
        offerers_factories.VenueFactory(managingOfferer=offerer_with_virtual_offer)
        offers_factories.OfferFactory(venue=virtual_venue)

        # Rejected offerer => venue should not ve returned
        rejected_offerer = offerers_factories.RejectedOffererFactory()
        offerers_factories.VenueFactory(managingOfferer=rejected_offerer)

        # Rejected offerer with validation date => venue should not ve returned
        rejected_offerer_after_validation = offerers_factories.RejectedOffererFactory(dateValidated=five_days_ago)
        offerers_factories.VenueFactory(managingOfferer=rejected_offerer_after_validation)

        venues = (
            repository.find_venues_of_offerers_with_no_offer_and_at_least_one_physical_venue_and_validated_x_days_ago(5)
            .order_by(models.Venue.id)
            .all()
        )
        expected_venues_list = [
            (venue_without_offer_1.id, venue_without_offer_1.bookingEmail),
            (venue_without_offer_2.id, venue_without_offer_2.bookingEmail),
        ]

        assert venues == expected_venues_list
