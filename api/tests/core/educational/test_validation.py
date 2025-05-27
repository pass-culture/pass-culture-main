import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from pcapi.core.educational import exceptions
from pcapi.core.educational.factories import CancelledCollectiveBookingFactory
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveStockFactory
from pcapi.core.educational.factories import ConfirmedCollectiveBookingFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.educational.factories import PendingCollectiveBookingFactory
from pcapi.core.educational.factories import UsedCollectiveBookingFactory
from pcapi.core.educational.models import EducationalDeposit
from pcapi.core.educational.validation import check_booking_limit_datetime
from pcapi.core.educational.validation import check_institution_fund
from pcapi.core.offerers import factories as offerers_factories


class EducationalValidationTest:
    def test_institution_fund_is_ok(self, db_session):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDeposit(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(1400.00),
        )
        PendingCollectiveBookingFactory(
            collectiveStock__price=Decimal(2000.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        CancelledCollectiveBookingFactory(
            collectiveStock__price=Decimal(2000.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        ConfirmedCollectiveBookingFactory.create_batch(
            20,
            collectiveStock__price=Decimal(20.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        UsedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )

        check_institution_fund(
            educational_institution.id, educational_year.adageId, Decimal(200.00), educational_deposit
        )

    def test_institution_fund_is_temporary_insufficient(self, db_session):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDeposit(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(1400.00),
            isFinal=False,
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        UsedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )

        with pytest.raises(exceptions.InsufficientTemporaryFund):
            check_institution_fund(
                educational_institution.id, educational_year.adageId, Decimal(200.00), educational_deposit
            )

    def test_institution_fund_is_insufficient(self, db_session):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        educational_deposit = EducationalDeposit(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(400.00),
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )
        UsedCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )

        with pytest.raises(exceptions.InsufficientFund):
            check_institution_fund(
                educational_institution.id, educational_year.adageId, Decimal(200.00), educational_deposit
            )


class CheckBookingLimitDatetimeTest:
    def test_check_booking_limit_datetime_should_raise_because_booking_limit_is_one_hour_after(self):
        venue = offerers_factories.VenueFactory(departementCode=71)
        offer = CollectiveOfferFactory(venueId=venue.id)
        stock = CollectiveStockFactory(collectiveOfferId=offer.id)

        beginning_date = datetime.datetime(2024, 7, 19, 8)
        booking_limit_date = beginning_date + datetime.timedelta(hours=1)
        with pytest.raises(exceptions.EducationalException):
            check_booking_limit_datetime(stock, beginning=beginning_date, booking_limit_datetime=booking_limit_date)

    def test_check_booking_limit_datetime_should_raise(self):
        collective_stock = CollectiveStockFactory()

        beginning_date = datetime.datetime(2024, 7, 19, 8)
        booking_limit_date = beginning_date + datetime.timedelta(days=1)

        # with collective stock
        with pytest.raises(exceptions.EducationalException):
            check_booking_limit_datetime(
                collective_stock, beginning=beginning_date, booking_limit_datetime=booking_limit_date
            )

        with pytest.raises(exceptions.EducationalException):
            check_booking_limit_datetime(None, beginning=beginning_date, booking_limit_datetime=booking_limit_date)

    def test_check_booking_limit_datetime_should_not_raise_because_a_date_is_missing(self):
        stock = CollectiveStockFactory()

        beginning_date = datetime.datetime(2024, 7, 19, 8)
        booking_limit_date = beginning_date + datetime.timedelta(days=1)

        check_booking_limit_datetime(stock, beginning=None, booking_limit_datetime=booking_limit_date)
        check_booking_limit_datetime(stock, beginning=beginning_date, booking_limit_datetime=None)

    @pytest.mark.parametrize(
        "time_zone_expected",
        [
            ZoneInfo("America/Guadeloupe"),  #  "offer.venue.offererAddress.address.timezone",
            ZoneInfo("Europe/Paris"),  # "offer.venue.timezone",
        ],
    )
    def test_check_booking_limit_datetime_priorisation_order(self, time_zone_expected):
        oa = (
            offerers_factories.OffererAddressFactory(address__departmentCode="974", address__inseeCode="97410")
            if time_zone_expected == ZoneInfo("Indian/Reunion")
            else None
        )
        if time_zone_expected in [ZoneInfo("Indian/Reunion"), ZoneInfo("America/Guadeloupe")]:
            venue = offerers_factories.VenueFactory(
                departementCode=71,
                offererAddress__address__departmentCode="971",
                offererAddress__address__inseeCode="97103",
                offererAddress__address__timezone="America/Guadeloupe",
            )  # oa guadeloupe venue#france
        else:
            venue = offerers_factories.VirtualVenueFactory(departementCode=71)
        offer = CollectiveOfferFactory(offererAddress=oa, venue=venue)  # reunion
        stock = CollectiveStockFactory(collectiveOffer=offer)
        beginning_date = datetime.datetime(2024, 7, 19, 8, tzinfo=datetime.timezone.utc)
        booking_limit_date = beginning_date - datetime.timedelta(hours=1)

        # It's ok to ignore the tuple unpacking warning here because we are testing the value of beginning
        # and it should fails if check_booking_limit_datetime returns an empty list
        beginning, booking_limit_datetime = check_booking_limit_datetime(
            stock, beginning=beginning_date, booking_limit_datetime=booking_limit_date
        )
        assert beginning.tzinfo == booking_limit_datetime.tzinfo == time_zone_expected
