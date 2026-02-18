import datetime
import decimal
import typing


if typing.TYPE_CHECKING:
    from pcapi.core.bookings import models


# These Protocols can be used to type the result of a Query
# See _create_export_query, _get_filtered_booking_report, _get_filtered_booking_pro in repository
class ExportBookingsQueryResult(typing.Protocol):
    id: int
    venueName: str
    offerName: str
    stockBeginningDatetime: datetime.datetime | None
    offerId: int
    ean: str | None
    beneficiaryFirstName: str | None
    beneficiaryLastName: str | None
    beneficiaryEmail: str
    beneficiaryPhoneNumber: str | None
    beneficiaryPostalCode: str | None
    token: str
    priceCategoryLabel: str | None
    amount: decimal.Decimal
    quantity: int
    status: "models.BookingStatus"
    bookedAt: datetime.datetime
    usedAt: datetime.datetime | None
    reimbursedAt: datetime.datetime | None
    cancelledAt: datetime.datetime | None
    isExternal: bool
    isConfirmed: bool
    is_caledonian: bool
    userId: int
    offerDepartmentCode: str | None
    venueDepartmentCode: str
    locationName: str | None
    locationStreet: int | None
    locationPostalCode: int | None
    locationCity: int | None


class GetBookingsQueryResult(typing.Protocol):
    bookingToken: str
    bookedAt: datetime.datetime
    quantity: int
    bookingAmount: decimal.Decimal
    priceCategoryLabel: str | None
    usedAt: datetime.datetime | None
    cancelledAt: datetime.datetime | None
    cancellationLimitDate: datetime.datetime | None
    status: "models.BookingStatus"
    reimbursedAt: datetime.datetime | None
    isExternal: bool
    isConfirmed: bool
    offerName: str
    offerId: int
    offerEan: str | None
    beneficiaryFirstname: str | None
    beneficiaryLastname: str | None
    beneficiaryEmail: str
    beneficiaryPhoneNumber: str | None
    stockBeginningDatetime: datetime.datetime | None
    stockId: int
    offerDepartmentCode: str | None
    venueDepartmentCode: str
