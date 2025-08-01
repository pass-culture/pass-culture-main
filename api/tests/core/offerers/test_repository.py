from datetime import datetime
from datetime import timedelta

import pytest
import sqlalchemy.orm as sa_orm

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import exceptions
from pcapi.core.offerers import models
from pcapi.core.offerers import repository
from pcapi.core.offerers import schemas
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
        offerers_factories.NewUserOffererFactory(user=pro)
        assert repository.get_all_offerers_for_user(user=pro).all() == []

    def should_not_return_deactivated_offerers(self) -> None:
        # Given
        admin = users_factories.AdminFactory()
        offerers_factories.OffererFactory(isActive=False)

        # When
        offerers = repository.get_all_offerers_for_user(user=admin).all()

        # Then
        assert len(offerers) == 0

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
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer_with_only_virtual_venue)

        # Offerer with two physical venues and no offer => venus should be returned
        offerer_with_physical_venue = offerers_factories.OffererFactory(dateValidated=five_days_ago)
        venue_without_offer_1 = offerers_factories.VenueFactory(managingOfferer=offerer_with_physical_venue)
        venue_without_offer_2 = offerers_factories.VenueFactory(managingOfferer=offerer_with_physical_venue)

        # Offerer with virtual venue and one offer => venue should not be returned
        offerer_with_virtual_offer = offerers_factories.OffererFactory(dateValidated=five_days_ago)
        virtual_venue = offerers_factories.VirtualVenueFactory(managingOfferer=offerer_with_virtual_offer)
        offerers_factories.VenueFactory(managingOfferer=offerer_with_virtual_offer)
        offers_factories.OfferFactory(venue=virtual_venue)

        # Rejected offerer => venue should not ve returned
        rejected_offerer = offerers_factories.RejectedOffererFactory()
        offerers_factories.VenueFactory(managingOfferer=rejected_offerer)

        # Rejected offerer with validation date => venue should not ve returned
        rejected_offerer_after_validation = offerers_factories.RejectedOffererFactory(dateValidated=five_days_ago)
        offerers_factories.VenueFactory(managingOfferer=rejected_offerer_after_validation)

        # Offerer with two physical venues and one collective offer => venues should not be returned
        offerer_with_two_venues = offerers_factories.OffererFactory(dateValidated=five_days_ago)
        venue_with_offers = offerers_factories.VenueFactory(managingOfferer=offerer_with_two_venues)
        offerers_factories.VenueFactory(managingOfferer=offerer_with_two_venues)
        educational_factories.CollectiveOfferFactory(venue=venue_with_offers)

        # Offerer with two physical venues and one collective template offer => venues should not be returned
        offerer_with_two_venues = offerers_factories.OffererFactory(dateValidated=five_days_ago)
        venue_with_offers = offerers_factories.VenueFactory(managingOfferer=offerer_with_two_venues)
        offerers_factories.VenueFactory(managingOfferer=offerer_with_two_venues)
        educational_factories.CollectiveOfferTemplateFactory(venue=venue_with_offers)

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


class GetOffererAddressesTest:
    @pytest.mark.parametrize(
        "offer_factory,with_offers_option",
        (
            (offers_factories.OfferFactory, schemas.GetOffererAddressesWithOffersOption.INDIVIDUAL_OFFERS_ONLY),
            (
                educational_factories.CollectiveOfferOnOtherAddressLocationFactory,
                schemas.GetOffererAddressesWithOffersOption.COLLECTIVE_OFFERS_ONLY,
            ),
            (
                educational_factories.CollectiveOfferTemplateOnOtherAddressLocationFactory,
                schemas.GetOffererAddressesWithOffersOption.COLLECTIVE_OFFER_TEMPLATES_ONLY,
            ),
        ),
    )
    def test_get_offerer_addresses(self, offer_factory, with_offers_option):
        offerer = offerers_factories.OffererFactory()
        venue_with_two_offers = offerers_factories.VenueFactory(managingOfferer=offerer)
        # Shouldn't appear in the results
        offerers_factories.OffererAddressFactory(offerer=offerer)
        # Should appear in the results
        offerer_address_with_one_offer = offerers_factories.OffererAddressFactory(offerer=offerer)
        # Ensure that we don't return an OffererAddress for every associated offer
        offerer_address_with_two_offers = offerers_factories.OffererAddressFactory(offerer=offerer)

        offer_factory(venue__managingOfferer=offerer, offererAddress=offerer_address_with_one_offer)
        offer_factory(venue=venue_with_two_offers, offererAddress=offerer_address_with_two_offers)
        offer_factory(venue=venue_with_two_offers, offererAddress=offerer_address_with_two_offers)

        query = repository.get_offerer_addresses(offerer_id=offerer.id, with_offers_option=with_offers_option)

        results = query.all()
        assert len(results) == 2
        assert {r.id for r in results} == {offerer_address_with_one_offer.id, offerer_address_with_two_offers.id}

    def test_get_offerer_addresses_offer_types(self):
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        oa = offerers_factories.OffererAddressFactory(offerer=offerer)
        other_oa = offerers_factories.OffererAddressFactory(offerer=offerer)

        offers_factories.OfferFactory(venue=venue, offererAddress=oa)
        educational_factories.CollectiveOfferOnOtherAddressLocationFactory(venue=venue, offererAddress=other_oa)
        educational_factories.CollectiveOfferTemplateOnOtherAddressLocationFactory(venue=venue, offererAddress=other_oa)

        query = repository.get_offerer_addresses(
            offerer_id=offerer.id, with_offers_option=schemas.GetOffererAddressesWithOffersOption.INDIVIDUAL_OFFERS_ONLY
        )
        result = query.one()
        assert result.id == oa.id


class GetOffererHeadlineOfferTest:
    def test_return_headline_offer(self):
        offer = offers_factories.OfferFactory()
        offers_factories.HeadlineOfferFactory(offer=offer)

        headline_offer = repository.get_offerer_headline_offer(offer.venue.managingOffererId)

        assert headline_offer.id == offer.id

    def test_shoud_not_return_several_headline_offer(self):
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        other_venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = offers_factories.OfferFactory(venue=venue)
        other_offer = offers_factories.OfferFactory(venue=other_venue)
        offers_factories.HeadlineOfferFactory(offer=offer, venue=venue)
        offers_factories.HeadlineOfferFactory(offer=other_offer, venue=other_venue)

        with pytest.raises(sa_orm.exc.MultipleResultsFound):
            repository.get_offerer_headline_offer(offerer.id)

    def test_returns_no_headline_offer(self):
        offerer = offerers_factories.OffererFactory()

        with pytest.raises(sa_orm.exc.NoResultFound):
            repository.get_offerer_headline_offer(offerer.id)
