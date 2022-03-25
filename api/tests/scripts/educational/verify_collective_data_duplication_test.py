from datetime import datetime

import pytest

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.offers.factories import EducationalEventOfferFactory
from pcapi.core.offers.factories import EducationalEventStockFactory
from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.scripts.educational.verify_collective_data_duplication import verify_collective_bookings_duplication
from pcapi.scripts.educational.verify_collective_data_duplication import verify_collective_data_duplication
from pcapi.scripts.educational.verify_collective_data_duplication import verify_collective_offers_duplication
from pcapi.scripts.educational.verify_collective_data_duplication import verify_collective_stocks_duplication


@pytest.mark.usefixtures("db_session")
class VerifyCollectiveOffersDuplicationTest:
    def should_return_true_if_there_are_no_difference_and_data_is_present_in_db(self):
        # Given
        educational_offer = EducationalEventOfferFactory(
            extraData={
                "students": ["Collège - 4e", "CAP - 1re année"],
                "contactEmail": "contact@email.com",
                "contactPhone": "0601020304",
                "offerVenue": {"addressType": "school", "otherAddress": "", "venueId": ""},
            }
        )
        educational_offer2 = EducationalEventOfferFactory(
            extraData={
                "students": ["Collège - 3e"],
                "contactEmail": "contact2@email.com",
                "contactPhone": "0605060708",
                "offerVenue": {"addressType": "other", "otherAddress": "chez moi", "venueId": ""},
            }
        )
        educational_stock = EducationalEventStockFactory(
            offer__extraData={
                "students": ["Collège - 3e"],
                "contactEmail": "contact2@email.com",
                "contactPhone": "0605060708",
                "offerVenue": {"addressType": "other", "otherAddress": "chez moi", "venueId": ""},
                "isShowcase": True,
            },
            educationalPriceDetail="le détail du prix",
        )
        educational_offer3 = educational_stock.offer

        factories.CollectiveOfferFactory(
            offerId=educational_offer.id,
            isActive=educational_offer.isActive,
            venue=educational_offer.venue,
            name=educational_offer.name,
            bookingEmail=educational_offer.bookingEmail,
            description=educational_offer.description,
            durationMinutes=educational_offer.durationMinutes,
            subcategoryId=educational_offer.subcategoryId,
            students=[models.StudentLevels.CAP1, models.StudentLevels.COLLEGE4],
            contactEmail="contact@email.com",
            contactPhone="0601020304",
            offerVenue={"addressType": "school", "otherAddress": "", "venueId": ""},
        )
        factories.CollectiveOfferFactory(
            offerId=educational_offer2.id,
            isActive=educational_offer2.isActive,
            venue=educational_offer2.venue,
            name=educational_offer2.name,
            bookingEmail=educational_offer2.bookingEmail,
            description=educational_offer2.description,
            durationMinutes=educational_offer2.durationMinutes,
            subcategoryId=educational_offer2.subcategoryId,
            students=[models.StudentLevels.COLLEGE3],
            contactEmail="contact2@email.com",
            contactPhone="0605060708",
            offerVenue={"addressType": "other", "otherAddress": "chez moi", "venueId": ""},
        )
        factories.CollectiveOfferTemplateFactory(
            offerId=educational_offer3.id,
            isActive=educational_offer3.isActive,
            venue=educational_offer3.venue,
            name=educational_offer3.name,
            bookingEmail=educational_offer3.bookingEmail,
            description=educational_offer3.description,
            durationMinutes=educational_offer3.durationMinutes,
            subcategoryId=educational_offer3.subcategoryId,
            students=[models.StudentLevels.COLLEGE3],
            contactEmail="contact2@email.com",
            contactPhone="0605060708",
            offerVenue={"addressType": "other", "otherAddress": "chez moi", "venueId": ""},
            priceDetail=educational_stock.educationalPriceDetail,
        )

        # When
        (
            success,
            missing_collective_offer_templates_offer_ids,
            invalid_collective_offer_templates_offer_ids,
            missing_collective_offers_offer_ids,
            invalid_collective_offers_offer_ids,
        ) = verify_collective_offers_duplication()

        # Then
        assert success == True
        assert missing_collective_offer_templates_offer_ids == []
        assert invalid_collective_offer_templates_offer_ids == []
        assert missing_collective_offers_offer_ids == []
        assert invalid_collective_offers_offer_ids == []

    def should_return_false_if_at_least_one_element_does_not_match_original_offer(self):
        # Given
        educational_offer = EducationalEventOfferFactory(
            extraData={
                "students": ["Collège - 4e", "CAP - 1re année"],
                "contactEmail": "contact@email.com",
                "contactPhone": "0601020304",
                "offerVenue": {"addressType": "school", "otherAddress": "", "venueId": ""},
            },
            name="Offre 1",
        )
        educational_offer2 = EducationalEventOfferFactory(
            extraData={
                "students": ["Collège - 3e"],
                "contactEmail": "contact2@email.com",
                "contactPhone": "0605060708",
                "offerVenue": {"addressType": "other", "otherAddress": "chez moi", "venueId": ""},
            },
            bookingEmail="booking@email.com",
        )
        educational_stock = EducationalEventStockFactory(
            offer__extraData={
                "students": ["Collège - 3e"],
                "contactEmail": "contact2@email.com",
                "contactPhone": "0605060708",
                "offerVenue": {"addressType": "other", "otherAddress": "chez moi", "venueId": ""},
                "isShowcase": True,
            },
            offer__description="Une description",
        )
        educational_offer3 = educational_stock.offer
        educational_offer4 = EducationalEventOfferFactory(
            extraData={
                "students": ["Collège - 3e"],
                "contactEmail": "contact@email.com",
                "contactPhone": "0601020304",
                "offerVenue": {"addressType": "school", "otherAddress": "", "venueId": ""},
            },
            durationMinutes=10,
        )
        educational_offer5 = EducationalEventOfferFactory(
            extraData={
                "students": ["Collège - 3e"],
                "contactEmail": "contact@email.com",
                "contactPhone": "0601020304",
                "offerVenue": {"addressType": "school", "otherAddress": "", "venueId": ""},
            },
            subcategoryId="CINE_PLEIN_AIR",
        )
        educational_offer6 = EducationalEventOfferFactory(
            extraData={
                "students": ["Collège - 3e"],
                "contactEmail": "contact@email.com",
                "contactPhone": "0601020304",
                "offerVenue": {"addressType": "school", "otherAddress": "", "venueId": ""},
            },
        )
        educational_offer7 = EducationalEventOfferFactory(
            extraData={
                "students": ["Collège - 3e"],
                "contactEmail": "contact@email.com",
                "contactPhone": "0601020304",
                "offerVenue": {"addressType": "school", "otherAddress": "", "venueId": ""},
            },
        )
        educational_offer8 = EducationalEventOfferFactory(
            extraData={
                "students": ["Collège - 3e"],
                "contactEmail": "contact@email.com",
                "contactPhone": "0601020304",
                "offerVenue": {"addressType": "school", "otherAddress": "", "venueId": ""},
            },
        )
        educational_offer9 = EducationalEventOfferFactory(
            extraData={
                "students": ["Collège - 3e"],
                "contactEmail": "contact@email.com",
                "contactPhone": "0601020304",
                "offerVenue": {"addressType": "school", "otherAddress": "", "venueId": ""},
            },
        )
        educational_stock2 = EducationalEventStockFactory(
            offer__extraData={
                "students": ["Collège - 3e"],
                "contactEmail": "contact2@email.com",
                "contactPhone": "0605060708",
                "offerVenue": {"addressType": "other", "otherAddress": "chez moi", "venueId": ""},
                "isShowcase": True,
            },
            educationalPriceDetail="Un détail",
        )
        educational_offer10 = educational_stock2.offer

        factories.CollectiveOfferFactory(
            offerId=educational_offer.id,
            isActive=educational_offer.isActive,
            venue=educational_offer.venue,
            name="Pas pareil qu'Offre 1",
            bookingEmail=educational_offer.bookingEmail,
            description=educational_offer.description,
            durationMinutes=educational_offer.durationMinutes,
            subcategoryId=educational_offer.subcategoryId,
            students=[models.StudentLevels.CAP1, models.StudentLevels.COLLEGE4],
            contactEmail="contact@email.com",
            contactPhone="0601020304",
            offerVenue={"addressType": "school", "otherAddress": "", "venueId": ""},
        )
        factories.CollectiveOfferFactory(
            offerId=educational_offer2.id,
            isActive=educational_offer2.isActive,
            venue=educational_offer2.venue,
            name=educational_offer2.name,
            bookingEmail="mauvaisbooking@email.com",
            description=educational_offer2.description,
            durationMinutes=educational_offer2.durationMinutes,
            subcategoryId=educational_offer2.subcategoryId,
            students=[models.StudentLevels.COLLEGE3],
            contactEmail="contact2@email.com",
            contactPhone="0605060708",
            offerVenue={"addressType": "other", "otherAddress": "chez moi", "venueId": ""},
        )
        factories.CollectiveOfferTemplateFactory(
            offerId=educational_offer3.id,
            isActive=educational_offer3.isActive,
            venue=educational_offer3.venue,
            name=educational_offer3.name,
            bookingEmail=educational_offer3.bookingEmail,
            description="Une autre description",
            durationMinutes=educational_offer3.durationMinutes,
            subcategoryId=educational_offer3.subcategoryId,
            students=[models.StudentLevels.COLLEGE3],
            contactEmail="contact2@email.com",
            contactPhone="0605060708",
            offerVenue={"addressType": "other", "otherAddress": "chez moi", "venueId": ""},
            priceDetail=educational_stock.educationalPriceDetail,
        )
        factories.CollectiveOfferFactory(
            offerId=educational_offer4.id,
            isActive=educational_offer4.isActive,
            venue=educational_offer4.venue,
            name=educational_offer4.name,
            bookingEmail=educational_offer4.bookingEmail,
            description=educational_offer4.description,
            durationMinutes=20,
            subcategoryId=educational_offer4.subcategoryId,
            students=[models.StudentLevels.COLLEGE3],
            contactEmail="contact2@email.com",
            contactPhone="0605060708",
            offerVenue={"addressType": "other", "otherAddress": "chez moi", "venueId": ""},
        )
        factories.CollectiveOfferFactory(
            offerId=educational_offer5.id,
            isActive=educational_offer5.isActive,
            venue=educational_offer5.venue,
            name=educational_offer5.name,
            bookingEmail=educational_offer5.bookingEmail,
            description=educational_offer5.description,
            durationMinutes=educational_offer5.durationMinutes,
            subcategoryId="EVENEMENT_CINE",
            students=[models.StudentLevels.COLLEGE3],
            contactEmail="contact2@email.com",
            contactPhone="0605060708",
            offerVenue={"addressType": "other", "otherAddress": "chez moi", "venueId": ""},
        )
        factories.CollectiveOfferFactory(
            offerId=educational_offer6.id,
            isActive=educational_offer6.isActive,
            venue=educational_offer6.venue,
            name=educational_offer6.name,
            bookingEmail=educational_offer6.bookingEmail,
            description=educational_offer6.description,
            durationMinutes=educational_offer6.durationMinutes,
            subcategoryId=educational_offer6.subcategoryId,
            students=[models.StudentLevels.CAP1],
            contactEmail="contact2@email.com",
            contactPhone="0605060708",
            offerVenue={"addressType": "other", "otherAddress": "chez moi", "venueId": ""},
        )
        factories.CollectiveOfferFactory(
            offerId=educational_offer7.id,
            isActive=educational_offer7.isActive,
            venue=educational_offer7.venue,
            name=educational_offer7.name,
            bookingEmail=educational_offer7.bookingEmail,
            description=educational_offer7.description,
            durationMinutes=educational_offer7.durationMinutes,
            subcategoryId=educational_offer7.subcategoryId,
            students=[models.StudentLevels.COLLEGE3],
            contactEmail="mauvaiscontact@email.com",
            contactPhone="0605060708",
            offerVenue={"addressType": "other", "otherAddress": "chez moi", "venueId": ""},
        )
        factories.CollectiveOfferFactory(
            offerId=educational_offer8.id,
            isActive=educational_offer8.isActive,
            venue=educational_offer8.venue,
            name=educational_offer8.name,
            bookingEmail=educational_offer8.bookingEmail,
            description=educational_offer8.description,
            durationMinutes=educational_offer8.durationMinutes,
            subcategoryId=educational_offer8.subcategoryId,
            students=[models.StudentLevels.COLLEGE3],
            contactEmail="mauvaiscontact@email.com",
            contactPhone="0000000000",
            offerVenue={"addressType": "other", "otherAddress": "chez moi", "venueId": ""},
        )
        factories.CollectiveOfferFactory(
            offerId=educational_offer9.id,
            isActive=educational_offer9.isActive,
            venue=educational_offer9.venue,
            name=educational_offer9.name,
            bookingEmail=educational_offer9.bookingEmail,
            description=educational_offer9.description,
            durationMinutes=educational_offer9.durationMinutes,
            subcategoryId=educational_offer9.subcategoryId,
            students=[models.StudentLevels.COLLEGE3],
            contactEmail="mauvaiscontact@email.com",
            contactPhone="0000000000",
            offerVenue={"addressType": "offererVenue", "otherAddress": "chez moi", "venueId": "VENUE_ID"},
        )
        factories.CollectiveOfferTemplateFactory(
            offerId=educational_offer10.id,
            isActive=educational_offer10.isActive,
            venue=educational_offer10.venue,
            name=educational_offer10.name,
            bookingEmail=educational_offer10.bookingEmail,
            description=educational_offer10.description,
            durationMinutes=educational_offer10.durationMinutes,
            subcategoryId=educational_offer10.subcategoryId,
            students=[models.StudentLevels.COLLEGE3],
            contactEmail="mauvaiscontact@email.com",
            contactPhone="0000000000",
            offerVenue={"addressType": "other", "otherAddress": "chez moi", "venueId": ""},
            priceDetail="Un mauvais détail",
        )

        # When
        (
            success,
            missing_collective_offer_templates_offer_ids,
            invalid_collective_offer_templates_offer_ids,
            missing_collective_offers_offer_ids,
            invalid_collective_offers_offer_ids,
        ) = verify_collective_offers_duplication()

        # Then
        assert success == False
        assert missing_collective_offer_templates_offer_ids == []
        assert set(invalid_collective_offer_templates_offer_ids) == set([educational_offer3.id, educational_offer10.id])
        assert missing_collective_offers_offer_ids == []
        assert set(invalid_collective_offers_offer_ids) == set(
            [
                educational_offer.id,
                educational_offer2.id,
                educational_offer4.id,
                educational_offer5.id,
                educational_offer6.id,
                educational_offer7.id,
                educational_offer8.id,
                educational_offer9.id,
            ]
        )

    def should_fail_when_collective_offer_is_missing(self):
        # Given
        educational_offer1 = EducationalEventOfferFactory()
        educational_offer2 = EducationalEventOfferFactory(extraData={"isShowcase": True})

        # When
        (
            success,
            missing_collective_offer_templates_offer_ids,
            invalid_collective_offer_templates_offer_ids,
            missing_collective_offers_offer_ids,
            invalid_collective_offers_offer_ids,
        ) = verify_collective_offers_duplication()

        assert success == False
        assert missing_collective_offer_templates_offer_ids == [educational_offer2.id]
        assert invalid_collective_offer_templates_offer_ids == []
        assert missing_collective_offers_offer_ids == [educational_offer1.id]
        assert invalid_collective_offers_offer_ids == []


@pytest.mark.usefixtures("db_session")
class VerifyCollectiveStocksDuplicationTest:
    def should_return_true_if_there_are_no_difference_and_data_is_present_in_db(self):
        # Given
        educational_stock = EducationalEventStockFactory()
        factories.CollectiveStockFactory(
            beginningDatetime=educational_stock.beginningDatetime,
            price=educational_stock.price,
            bookingLimitDatetime=educational_stock.bookingLimitDatetime,
            numberOfTickets=educational_stock.numberOfTickets,
            priceDetail=educational_stock.educationalPriceDetail,
            stockId=educational_stock.id,
        )

        # When
        (
            success,
            missing_collective_stocks_stock_ids,
            invalid_collective_stocks_stock_ids,
        ) = verify_collective_stocks_duplication()

        # Then
        assert success == True
        assert missing_collective_stocks_stock_ids == []
        assert invalid_collective_stocks_stock_ids == []

    def should_return_False_when_data_does_not_match_original_stock(self):
        # Given
        educational_stock1 = EducationalEventStockFactory(beginningDatetime=datetime(2022, 6, 12, 10, 0, 0))
        educational_stock2 = EducationalEventStockFactory(price=100)
        educational_stock3 = EducationalEventStockFactory(
            beginningDatetime=datetime(2022, 6, 12, 10, 0, 0), bookingLimitDatetime=datetime(2022, 6, 12, 10, 0, 0)
        )
        educational_stock4 = EducationalEventStockFactory(numberOfTickets=10)
        educational_stock5 = EducationalEventStockFactory(educationalPriceDetail="Détail")

        factories.CollectiveStockFactory(
            beginningDatetime=datetime(2022, 8, 14, 12, 0, 0),
            price=educational_stock1.price,
            bookingLimitDatetime=educational_stock1.bookingLimitDatetime,
            numberOfTickets=educational_stock1.numberOfTickets,
            priceDetail=educational_stock1.educationalPriceDetail,
            stockId=educational_stock1.id,
        )
        factories.CollectiveStockFactory(
            beginningDatetime=educational_stock2.beginningDatetime,
            price=200,
            bookingLimitDatetime=educational_stock2.bookingLimitDatetime,
            numberOfTickets=educational_stock2.numberOfTickets,
            priceDetail=educational_stock2.educationalPriceDetail,
            stockId=educational_stock2.id,
        )
        factories.CollectiveStockFactory(
            beginningDatetime=educational_stock3.beginningDatetime,
            price=educational_stock3.price,
            bookingLimitDatetime=datetime(2022, 6, 10, 12, 0, 0),
            numberOfTickets=educational_stock3.numberOfTickets,
            priceDetail=educational_stock3.educationalPriceDetail,
            stockId=educational_stock3.id,
        )
        factories.CollectiveStockFactory(
            beginningDatetime=educational_stock4.beginningDatetime,
            price=educational_stock4.price,
            bookingLimitDatetime=educational_stock4.bookingLimitDatetime,
            numberOfTickets=30,
            priceDetail=educational_stock4.educationalPriceDetail,
            stockId=educational_stock4.id,
        )
        factories.CollectiveStockFactory(
            beginningDatetime=educational_stock5.beginningDatetime,
            price=educational_stock5.price,
            bookingLimitDatetime=educational_stock5.bookingLimitDatetime,
            numberOfTickets=educational_stock5.numberOfTickets,
            priceDetail="Mauvais détail",
            stockId=educational_stock5.id,
        )

        # When
        (
            success,
            missing_collective_stocks_stock_ids,
            invalid_collective_stocks_stock_ids,
        ) = verify_collective_stocks_duplication()

        # Then
        assert success == False
        assert missing_collective_stocks_stock_ids == []
        assert set(invalid_collective_stocks_stock_ids) == set(
            [
                educational_stock1.id,
                educational_stock2.id,
                educational_stock3.id,
                educational_stock4.id,
                educational_stock5.id,
            ]
        )

    def should_return_False_if_data_is_missing(self):
        # Given
        educational_stock = EducationalEventStockFactory()

        # When
        (
            success,
            missing_collective_stocks_stock_ids,
            invalid_collective_stocks_stock_ids,
        ) = verify_collective_stocks_duplication()

        # Then
        assert success == False
        assert missing_collective_stocks_stock_ids == [educational_stock.id]
        assert invalid_collective_stocks_stock_ids == []


@pytest.mark.usefixtures("db_session")
class VerifyCollectiveBookingsDuplicationTest:
    def should_return_true_if_there_are_no_difference_and_data_is_present_in_db(self):
        # Given
        educational_booking = EducationalBookingFactory(
            status=BookingStatus.CONFIRMED.name, cancellationReason=BookingCancellationReasons.FRAUD.name
        )
        factories.CollectiveBookingFactory(
            dateUsed=educational_booking.dateUsed,
            venue=educational_booking.venue,
            offerer=educational_booking.offerer,
            cancellationDate=educational_booking.cancellationDate,
            cancellationLimitDate=educational_booking.cancellationLimitDate,
            cancellationReason=models.CollectiveBookingCancellationReasons.FRAUD.name,
            status=models.CollectiveBookingStatus.CONFIRMED.name,
            reimbursementDate=educational_booking.reimbursementDate,
            educationalInstitution=educational_booking.educationalBooking.educationalInstitution,
            educationalYear=educational_booking.educationalBooking.educationalYear,
            confirmationDate=educational_booking.educationalBooking.confirmationDate,
            confirmationLimitDate=educational_booking.educationalBooking.confirmationLimitDate,
            educationalRedactor=educational_booking.educationalBooking.educationalRedactor,
            bookingId=educational_booking.id,
        )

        # When
        (
            success,
            missing_collective_bookings_booking_ids,
            invalid_collective_bookings_booking_ids,
        ) = verify_collective_bookings_duplication()

        # Then
        assert success == True
        assert missing_collective_bookings_booking_ids == []
        assert invalid_collective_bookings_booking_ids == []

    def should_return_False_when_data_does_not_match_original_stock(self):
        # Given
        offerer = OffererFactory()
        offerer2 = OffererFactory()
        venue = VenueFactory(managingOfferer=offerer)
        venue2 = VenueFactory(managingOfferer=offerer2)
        educational_year = factories.EducationalYearFactory()
        educational_year2 = factories.EducationalYearFactory()
        educational_institution = factories.EducationalInstitutionFactory()
        educational_institution2 = factories.EducationalInstitutionFactory()
        educational_redactor = factories.EducationalRedactorFactory()
        educational_redactor2 = factories.EducationalRedactorFactory()

        educational_booking1 = EducationalBookingFactory(
            dateUsed=datetime(2022, 7, 10),
            status=BookingStatus.CONFIRMED.name,
            cancellationReason=BookingCancellationReasons.OFFERER.name,
        )
        educational_booking2 = EducationalBookingFactory(
            venue=venue, status=BookingStatus.CONFIRMED.name, cancellationReason=BookingCancellationReasons.OFFERER.name
        )
        educational_booking3 = EducationalBookingFactory(
            offerer=offerer,
            status=BookingStatus.CONFIRMED.name,
            cancellationReason=BookingCancellationReasons.OFFERER.name,
        )
        educational_booking4 = EducationalBookingFactory(
            cancellationDate=datetime(2022, 7, 10),
            status=BookingStatus.CONFIRMED.name,
            cancellationReason=BookingCancellationReasons.OFFERER.name,
        )
        educational_booking5 = EducationalBookingFactory(
            cancellationLimitDate=datetime(2022, 7, 10),
            status=BookingStatus.CONFIRMED.name,
            cancellationReason=BookingCancellationReasons.OFFERER.name,
        )
        educational_booking6 = EducationalBookingFactory(
            status=BookingStatus.CONFIRMED.name, cancellationReason=BookingCancellationReasons.OFFERER.name
        )
        educational_booking7 = EducationalBookingFactory(
            status=BookingStatus.CONFIRMED.name, cancellationReason=BookingCancellationReasons.OFFERER.name
        )
        educational_booking8 = EducationalBookingFactory(
            reimbursementDate=datetime(2022, 7, 10),
            status=BookingStatus.CONFIRMED.name,
            cancellationReason=BookingCancellationReasons.OFFERER.name,
        )
        educational_booking9 = EducationalBookingFactory(
            educationalBooking__educationalInstitution=educational_institution,
            status=BookingStatus.CONFIRMED.name,
            cancellationReason=BookingCancellationReasons.OFFERER.name,
        )
        educational_booking10 = EducationalBookingFactory(
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.CONFIRMED.name,
            cancellationReason=BookingCancellationReasons.OFFERER.name,
        )
        educational_booking11 = EducationalBookingFactory(
            educationalBooking__confirmationDate=datetime(2022, 7, 10),
            status=BookingStatus.CONFIRMED.name,
            cancellationReason=BookingCancellationReasons.OFFERER.name,
        )
        educational_booking12 = EducationalBookingFactory(
            educationalBooking__confirmationLimitDate=datetime(2022, 7, 10),
            status=BookingStatus.CONFIRMED.name,
            cancellationReason=BookingCancellationReasons.OFFERER.name,
        )
        educational_booking13 = EducationalBookingFactory(
            educationalBooking__educationalRedactor=educational_redactor,
            status=BookingStatus.CONFIRMED.name,
            cancellationReason=BookingCancellationReasons.OFFERER.name,
        )

        factories.CollectiveBookingFactory(
            dateUsed=datetime(2022, 7, 11),
            venue=educational_booking1.venue,
            offerer=educational_booking1.offerer,
            cancellationDate=educational_booking1.cancellationDate,
            cancellationLimitDate=educational_booking1.cancellationLimitDate,
            cancellationReason=models.CollectiveBookingCancellationReasons.OFFERER,
            status=models.CollectiveBookingStatus.CONFIRMED,
            reimbursementDate=educational_booking1.reimbursementDate,
            educationalInstitution=educational_booking1.educationalBooking.educationalInstitution,
            educationalYear=educational_booking1.educationalBooking.educationalYear,
            confirmationDate=educational_booking1.educationalBooking.confirmationDate,
            confirmationLimitDate=educational_booking1.educationalBooking.confirmationLimitDate,
            educationalRedactor=educational_booking1.educationalBooking.educationalRedactor,
            bookingId=educational_booking1.id,
        )
        factories.CollectiveBookingFactory(
            dateUsed=educational_booking2.dateUsed,
            venue=venue2,
            offerer=educational_booking2.offerer,
            cancellationDate=educational_booking2.cancellationDate,
            cancellationLimitDate=educational_booking2.cancellationLimitDate,
            cancellationReason=models.CollectiveBookingCancellationReasons.OFFERER,
            status=models.CollectiveBookingStatus.CONFIRMED,
            reimbursementDate=educational_booking2.reimbursementDate,
            educationalInstitution=educational_booking2.educationalBooking.educationalInstitution,
            educationalYear=educational_booking2.educationalBooking.educationalYear,
            confirmationDate=educational_booking2.educationalBooking.confirmationDate,
            confirmationLimitDate=educational_booking2.educationalBooking.confirmationLimitDate,
            educationalRedactor=educational_booking2.educationalBooking.educationalRedactor,
            bookingId=educational_booking2.id,
        )
        factories.CollectiveBookingFactory(
            dateUsed=educational_booking3.dateUsed,
            venue=educational_booking3.venue,
            offerer=offerer2,
            cancellationDate=educational_booking3.cancellationDate,
            cancellationLimitDate=educational_booking3.cancellationLimitDate,
            cancellationReason=models.CollectiveBookingCancellationReasons.OFFERER,
            status=models.CollectiveBookingStatus.CONFIRMED,
            reimbursementDate=educational_booking3.reimbursementDate,
            educationalInstitution=educational_booking3.educationalBooking.educationalInstitution,
            educationalYear=educational_booking3.educationalBooking.educationalYear,
            confirmationDate=educational_booking3.educationalBooking.confirmationDate,
            confirmationLimitDate=educational_booking3.educationalBooking.confirmationLimitDate,
            educationalRedactor=educational_booking3.educationalBooking.educationalRedactor,
            bookingId=educational_booking3.id,
        )
        factories.CollectiveBookingFactory(
            dateUsed=educational_booking4.dateUsed,
            venue=educational_booking4.venue,
            offerer=educational_booking4.offerer,
            cancellationDate=datetime(2022, 7, 11),
            cancellationLimitDate=educational_booking4.cancellationLimitDate,
            cancellationReason=models.CollectiveBookingCancellationReasons.OFFERER,
            status=models.CollectiveBookingStatus.CONFIRMED,
            reimbursementDate=educational_booking4.reimbursementDate,
            educationalInstitution=educational_booking4.educationalBooking.educationalInstitution,
            educationalYear=educational_booking4.educationalBooking.educationalYear,
            confirmationDate=educational_booking4.educationalBooking.confirmationDate,
            confirmationLimitDate=educational_booking4.educationalBooking.confirmationLimitDate,
            educationalRedactor=educational_booking4.educationalBooking.educationalRedactor,
            bookingId=educational_booking4.id,
        )
        factories.CollectiveBookingFactory(
            dateUsed=educational_booking5.dateUsed,
            venue=educational_booking5.venue,
            offerer=educational_booking5.offerer,
            cancellationDate=educational_booking5.cancellationDate,
            cancellationLimitDate=datetime(2022, 7, 11),
            cancellationReason=models.CollectiveBookingCancellationReasons.OFFERER,
            status=models.CollectiveBookingStatus.CONFIRMED,
            reimbursementDate=educational_booking5.reimbursementDate,
            educationalInstitution=educational_booking5.educationalBooking.educationalInstitution,
            educationalYear=educational_booking5.educationalBooking.educationalYear,
            confirmationDate=educational_booking5.educationalBooking.confirmationDate,
            confirmationLimitDate=educational_booking5.educationalBooking.confirmationLimitDate,
            educationalRedactor=educational_booking5.educationalBooking.educationalRedactor,
            bookingId=educational_booking5.id,
        )
        factories.CollectiveBookingFactory(
            dateUsed=educational_booking6.dateUsed,
            venue=educational_booking6.venue,
            offerer=educational_booking6.offerer,
            cancellationDate=educational_booking6.cancellationDate,
            cancellationLimitDate=educational_booking6.cancellationLimitDate,
            cancellationReason=models.CollectiveBookingCancellationReasons.EXPIRED.name,
            status=models.CollectiveBookingStatus.CONFIRMED,
            reimbursementDate=educational_booking6.reimbursementDate,
            educationalInstitution=educational_booking6.educationalBooking.educationalInstitution,
            educationalYear=educational_booking6.educationalBooking.educationalYear,
            confirmationDate=educational_booking6.educationalBooking.confirmationDate,
            confirmationLimitDate=educational_booking6.educationalBooking.confirmationLimitDate,
            educationalRedactor=educational_booking6.educationalBooking.educationalRedactor,
            bookingId=educational_booking6.id,
        )
        factories.CollectiveBookingFactory(
            dateUsed=educational_booking7.dateUsed,
            venue=educational_booking7.venue,
            offerer=educational_booking7.offerer,
            cancellationDate=educational_booking7.cancellationDate,
            cancellationLimitDate=educational_booking7.cancellationLimitDate,
            cancellationReason=models.CollectiveBookingCancellationReasons.OFFERER,
            status=models.CollectiveBookingStatus.CANCELLED,
            reimbursementDate=educational_booking7.reimbursementDate,
            educationalInstitution=educational_booking7.educationalBooking.educationalInstitution,
            educationalYear=educational_booking7.educationalBooking.educationalYear,
            confirmationDate=educational_booking7.educationalBooking.confirmationDate,
            confirmationLimitDate=educational_booking7.educationalBooking.confirmationLimitDate,
            educationalRedactor=educational_booking7.educationalBooking.educationalRedactor,
            bookingId=educational_booking7.id,
        )
        factories.CollectiveBookingFactory(
            dateUsed=educational_booking8.dateUsed,
            venue=educational_booking8.venue,
            offerer=educational_booking8.offerer,
            cancellationDate=educational_booking8.cancellationDate,
            cancellationLimitDate=educational_booking8.cancellationLimitDate,
            cancellationReason=models.CollectiveBookingCancellationReasons.OFFERER,
            status=models.CollectiveBookingStatus.CONFIRMED,
            reimbursementDate=datetime(2022, 7, 11),
            educationalInstitution=educational_booking8.educationalBooking.educationalInstitution,
            educationalYear=educational_booking8.educationalBooking.educationalYear,
            confirmationDate=educational_booking8.educationalBooking.confirmationDate,
            confirmationLimitDate=educational_booking8.educationalBooking.confirmationLimitDate,
            educationalRedactor=educational_booking8.educationalBooking.educationalRedactor,
            bookingId=educational_booking8.id,
        )
        factories.CollectiveBookingFactory(
            dateUsed=educational_booking9.dateUsed,
            venue=educational_booking9.venue,
            offerer=educational_booking9.offerer,
            cancellationDate=educational_booking9.cancellationDate,
            cancellationLimitDate=educational_booking9.cancellationLimitDate,
            cancellationReason=models.CollectiveBookingCancellationReasons.OFFERER,
            status=models.CollectiveBookingStatus.CONFIRMED,
            reimbursementDate=educational_booking9.reimbursementDate,
            educationalInstitution=educational_institution2,
            educationalYear=educational_booking9.educationalBooking.educationalYear,
            confirmationDate=educational_booking9.educationalBooking.confirmationDate,
            confirmationLimitDate=educational_booking9.educationalBooking.confirmationLimitDate,
            educationalRedactor=educational_booking9.educationalBooking.educationalRedactor,
            bookingId=educational_booking9.id,
        )
        factories.CollectiveBookingFactory(
            dateUsed=educational_booking10.dateUsed,
            venue=educational_booking10.venue,
            offerer=educational_booking10.offerer,
            cancellationDate=educational_booking10.cancellationDate,
            cancellationLimitDate=educational_booking10.cancellationLimitDate,
            cancellationReason=models.CollectiveBookingCancellationReasons.OFFERER,
            status=models.CollectiveBookingStatus.CONFIRMED,
            reimbursementDate=educational_booking10.reimbursementDate,
            educationalInstitution=educational_booking10.educationalBooking.educationalInstitution,
            educationalYear=educational_year2,
            confirmationDate=educational_booking10.educationalBooking.confirmationDate,
            confirmationLimitDate=educational_booking10.educationalBooking.confirmationLimitDate,
            educationalRedactor=educational_booking10.educationalBooking.educationalRedactor,
            bookingId=educational_booking10.id,
        )
        factories.CollectiveBookingFactory(
            dateUsed=educational_booking11.dateUsed,
            venue=educational_booking11.venue,
            offerer=educational_booking11.offerer,
            cancellationDate=educational_booking11.cancellationDate,
            cancellationLimitDate=educational_booking11.cancellationLimitDate,
            cancellationReason=models.CollectiveBookingCancellationReasons.OFFERER,
            status=models.CollectiveBookingStatus.CONFIRMED,
            reimbursementDate=educational_booking11.reimbursementDate,
            educationalInstitution=educational_booking11.educationalBooking.educationalInstitution,
            educationalYear=educational_booking11.educationalBooking.educationalYear,
            confirmationDate=datetime(2022, 7, 11),
            confirmationLimitDate=educational_booking11.educationalBooking.confirmationLimitDate,
            educationalRedactor=educational_booking11.educationalBooking.educationalRedactor,
            bookingId=educational_booking11.id,
        )
        factories.CollectiveBookingFactory(
            dateUsed=educational_booking12.dateUsed,
            venue=educational_booking12.venue,
            offerer=educational_booking12.offerer,
            cancellationDate=educational_booking12.cancellationDate,
            cancellationLimitDate=educational_booking12.cancellationLimitDate,
            cancellationReason=models.CollectiveBookingCancellationReasons.OFFERER,
            status=models.CollectiveBookingStatus.CONFIRMED,
            reimbursementDate=educational_booking12.reimbursementDate,
            educationalInstitution=educational_booking12.educationalBooking.educationalInstitution,
            educationalYear=educational_booking12.educationalBooking.educationalYear,
            confirmationDate=educational_booking12.educationalBooking.confirmationDate,
            confirmationLimitDate=datetime(2022, 7, 11),
            educationalRedactor=educational_booking12.educationalBooking.educationalRedactor,
            bookingId=educational_booking12.id,
        )
        factories.CollectiveBookingFactory(
            dateUsed=educational_booking13.dateUsed,
            venue=educational_booking13.venue,
            offerer=educational_booking13.offerer,
            cancellationDate=educational_booking13.cancellationDate,
            cancellationLimitDate=educational_booking13.cancellationLimitDate,
            cancellationReason=models.CollectiveBookingCancellationReasons.OFFERER,
            status=models.CollectiveBookingStatus.CONFIRMED,
            reimbursementDate=educational_booking13.reimbursementDate,
            educationalInstitution=educational_booking13.educationalBooking.educationalInstitution,
            educationalYear=educational_booking13.educationalBooking.educationalYear,
            confirmationDate=educational_booking13.educationalBooking.confirmationDate,
            confirmationLimitDate=educational_booking13.educationalBooking.confirmationLimitDate,
            educationalRedactor=educational_redactor2,
            bookingId=educational_booking13.id,
        )
        # When
        (
            success,
            missing_collective_bookings_booking_ids,
            invalid_collective_bookings_booking_ids,
        ) = verify_collective_bookings_duplication()

        # Then
        assert success == False
        assert missing_collective_bookings_booking_ids == []
        assert set(invalid_collective_bookings_booking_ids) == set(
            [
                educational_booking1.id,
                educational_booking2.id,
                educational_booking3.id,
                educational_booking4.id,
                educational_booking5.id,
                educational_booking6.id,
                educational_booking7.id,
                educational_booking8.id,
                educational_booking9.id,
                educational_booking10.id,
                educational_booking11.id,
                educational_booking12.id,
                educational_booking13.id,
            ]
        )

    def should_return_False_if_data_is_missing(self):
        # Given
        educational_booking = EducationalBookingFactory(dateUsed=datetime(2022, 7, 10))

        # When
        (
            success,
            missing_collective_bookings_booking_ids,
            invalid_collective_bookings_booking_ids,
        ) = verify_collective_bookings_duplication()

        # Then
        assert success == False
        assert missing_collective_bookings_booking_ids == [educational_booking.id]
        assert invalid_collective_bookings_booking_ids == []


@pytest.mark.usefixtures("db_session")
class VerifyCollectiveDataDuplicationTest:
    def should_return_true(self):
        # Given
        educational_booking = EducationalBookingFactory(
            stock__offer__extraData={
                "contactEmail": "contact@email.com",
                "contactPhone": "0601020304",
                "offerVenue": {"addressType": "school", "otherAddress": "", "venueId": ""},
                "students": ["Collège - 4e", "CAP - 1re année"],
                "isShowcase": False,
            },
            cancellationReason=BookingCancellationReasons.FRAUD.name,
            status=BookingStatus.CONFIRMED.name,
        )
        factories.CollectiveBookingFactory(
            dateUsed=educational_booking.dateUsed,
            venue=educational_booking.venue,
            offerer=educational_booking.offerer,
            cancellationDate=educational_booking.cancellationDate,
            cancellationLimitDate=educational_booking.cancellationLimitDate,
            cancellationReason=models.CollectiveBookingCancellationReasons.FRAUD.name,
            status=models.CollectiveBookingStatus.CONFIRMED.name,
            reimbursementDate=educational_booking.reimbursementDate,
            educationalInstitution=educational_booking.educationalBooking.educationalInstitution,
            educationalYear=educational_booking.educationalBooking.educationalYear,
            confirmationDate=educational_booking.educationalBooking.confirmationDate,
            confirmationLimitDate=educational_booking.educationalBooking.confirmationLimitDate,
            educationalRedactor=educational_booking.educationalBooking.educationalRedactor,
            bookingId=educational_booking.id,
            # Collective stock
            collectiveStock__beginningDatetime=educational_booking.stock.beginningDatetime,
            collectiveStock__price=educational_booking.stock.price,
            collectiveStock__bookingLimitDatetime=educational_booking.stock.bookingLimitDatetime,
            collectiveStock__numberOfTickets=educational_booking.stock.numberOfTickets,
            collectiveStock__priceDetail=educational_booking.stock.educationalPriceDetail,
            collectiveStock__stockId=educational_booking.stock.id,
            # Collective offer
            collectiveStock__collectiveOffer__offerId=educational_booking.stock.offer.id,
            collectiveStock__collectiveOffer__isActive=educational_booking.stock.offer.isActive,
            collectiveStock__collectiveOffer__venue=educational_booking.stock.offer.venue,
            collectiveStock__collectiveOffer__name=educational_booking.stock.offer.name,
            collectiveStock__collectiveOffer__bookingEmail=educational_booking.stock.offer.bookingEmail,
            collectiveStock__collectiveOffer__description=educational_booking.stock.offer.description,
            collectiveStock__collectiveOffer__durationMinutes=educational_booking.stock.offer.durationMinutes,
            collectiveStock__collectiveOffer__subcategoryId=educational_booking.stock.offer.subcategoryId,
            collectiveStock__collectiveOffer__students=[models.StudentLevels.CAP1, models.StudentLevels.COLLEGE4],
            collectiveStock__collectiveOffer__contactEmail="contact@email.com",
            collectiveStock__collectiveOffer__contactPhone="0601020304",
            collectiveStock__collectiveOffer__offerVenue={"addressType": "school", "otherAddress": "", "venueId": ""},
        )

        # When
        success = verify_collective_data_duplication()

        # Then
        assert success == True

    def should_return_False_when_one_data_is_wrong(self):
        # Given
        educational_booking = EducationalBookingFactory(
            stock__offer__extraData={
                "contactEmail": "contact@email.com",
                "contactPhone": "0601020304",
                "offerVenue": {"addressType": "school", "otherAddress": "", "venueId": ""},
                "students": ["Collège - 4e", "CAP - 1re année"],
                "isShowcase": False,
            },
            cancellationReason=BookingCancellationReasons.FRAUD.name,
            status=BookingStatus.CONFIRMED.name,
        )
        factories.CollectiveBookingFactory(
            dateUsed=educational_booking.dateUsed,
            venue=educational_booking.venue,
            offerer=educational_booking.offerer,
            cancellationDate=educational_booking.cancellationDate,
            cancellationLimitDate=educational_booking.cancellationLimitDate,
            cancellationReason=models.CollectiveBookingCancellationReasons.FRAUD.name,
            status=models.CollectiveBookingStatus.CONFIRMED.name,
            reimbursementDate=educational_booking.reimbursementDate,
            educationalInstitution=educational_booking.educationalBooking.educationalInstitution,
            educationalYear=educational_booking.educationalBooking.educationalYear,
            confirmationDate=educational_booking.educationalBooking.confirmationDate,
            confirmationLimitDate=educational_booking.educationalBooking.confirmationLimitDate,
            educationalRedactor=educational_booking.educationalBooking.educationalRedactor,
            bookingId=educational_booking.id,
            # Collective stock
            collectiveStock__beginningDatetime=educational_booking.stock.beginningDatetime,
            collectiveStock__price=educational_booking.stock.price,
            collectiveStock__bookingLimitDatetime=educational_booking.stock.bookingLimitDatetime,
            collectiveStock__numberOfTickets=educational_booking.stock.numberOfTickets,
            collectiveStock__priceDetail=educational_booking.stock.educationalPriceDetail,
            collectiveStock__stockId=12345,  # WRONG ID
            # Collective offer
            collectiveStock__collectiveOffer__offerId=educational_booking.stock.offer.id,
            collectiveStock__collectiveOffer__isActive=educational_booking.stock.offer.isActive,
            collectiveStock__collectiveOffer__venue=educational_booking.stock.offer.venue,
            collectiveStock__collectiveOffer__name=educational_booking.stock.offer.name,
            collectiveStock__collectiveOffer__bookingEmail=educational_booking.stock.offer.bookingEmail,
            collectiveStock__collectiveOffer__description=educational_booking.stock.offer.description,
            collectiveStock__collectiveOffer__durationMinutes=educational_booking.stock.offer.durationMinutes,
            collectiveStock__collectiveOffer__subcategoryId=educational_booking.stock.offer.subcategoryId,
            collectiveStock__collectiveOffer__students=[models.StudentLevels.CAP1, models.StudentLevels.COLLEGE4],
            collectiveStock__collectiveOffer__contactEmail="contact@email.com",
            collectiveStock__collectiveOffer__contactPhone="0601020304",
            collectiveStock__collectiveOffer__offerVenue={"addressType": "school", "otherAddress": "", "venueId": ""},
        )

        # When
        success = verify_collective_data_duplication()

        # Then
        assert success == False
