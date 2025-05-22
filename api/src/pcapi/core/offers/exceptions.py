import typing

from pcapi.core.core_exception import CoreException
from pcapi.models.api_errors import ApiErrors


class OfferException(CoreException):
    pass


class ImageValidationError(Exception):
    pass


class UnidentifiedImage(ImageValidationError):
    def __init__(self) -> None:
        super().__init__("Le fichier fourni n'est pas une image valide")


class FileSizeExceeded(ImageValidationError):
    def __init__(self, max_size: float | str) -> None:
        super().__init__(f"Utilisez une image dont le poids est inférieur à {self._natural_size(max_size)}")

    @staticmethod
    def _natural_size(value: float | str) -> str:
        """Format a number of bytes like a human readable filesize (e.g. 10 kB).
        Decimal suffixes (kB, MB) are used.
        Compatible with jinja2's `filesizeformat` filter.

        This function is a simplified version of naturalsize from :
        https://github.com/python-humanize/humanize/blob/main/src/humanize/filesize.py
        Examples:
            ```pycon
            >>> naturalsize(3000000)
            '3.0 MB'
            >>> naturalsize(300)
            '300B'
            >>> naturalsize(3000)
            '3.0 KB'
            >>> naturalsize(3000)
            '2.9 KB'
            ```
        """
        suffix = ("kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")

        base = 1000
        float_value = float(value)
        abs_bytes = abs(float_value)

        if int(abs_bytes) == 1:
            return f"{int(float_value)} Byte"
        if abs_bytes < base:
            return f"{int(float_value)} Bytes"

        for i, s in enumerate(suffix):
            unit = base ** (i + 2)
            if abs_bytes < unit:
                return ("%.1f" + " %s") % ((base * float_value / unit), s)

        return ("%.1f" + " %s") % ((base * float_value / unit), "YB")


class ImageTooSmall(ImageValidationError):
    def __init__(self, min_width: int | None, min_height: int | None) -> None:
        if min_width and min_height:
            super().__init__(f"Utilisez une image plus grande (supérieure à {min_width}px par {min_height}px)")
        elif min_width:
            super().__init__(f"Utilisez une image plus grande (supérieure à {min_width}px de large)")
        elif min_height:
            super().__init__(f"Utilisez une image plus grande (supérieure à {min_height}px de haut)")


class ImageTooLarge(ImageValidationError):
    def __init__(self, max_width: int | None, max_height: int | None):
        if max_width and not max_height:
            super().__init__(f"Utilisez une image plus petite (inférieure à {max_width}px de large)")
        elif max_height and not max_width:
            super().__init__(f"Utilisez une image plus petite (inférieure à {max_height}px de haut)")
        else:
            super().__init__(f"Utilisez une image plus petite (inférieure à {max_width}px par {max_height}px)")


class UnacceptedFileType(ImageValidationError):
    def __init__(self, accepted_types: typing.Iterable, image_format: str) -> None:
        super().__init__(
            f"Le format {image_format.lower()} n'est pas supporté. Utilisez un format {', '.join(accepted_types)}"
        )


class MissingImage(ImageValidationError):
    def __init__(self) -> None:
        super().__init__("Nous n'avons pas réceptionné l'image, merci d'essayer à nouveau.")


class ThumbnailStorageError(ApiErrors):
    status_code = 500


class StockDoesNotExist(ApiErrors):
    status_code = 400


class OfferReportError(Exception):
    code = "OFFER_REPORT_ERROR"


class OfferAlreadyReportedError(OfferReportError):
    code = "OFFER_ALREADY_REPORTED"


class ReportMalformed(OfferReportError):
    code = "REPORT_MALFORMED"


class BookingLimitDatetimeTooLate(OfferException):  # (tcoudray-pass, 14/05/2025) TODO: Remove
    def __init__(self) -> None:
        super().__init__()
        self.add_error("bookingLimitDatetime", "The bookingLimitDatetime must be before the beginning of the event")


class OfferNotFound(Exception):
    pass


class ProductNotFound(Exception):
    pass


class CollectiveStockNotFound(Exception):
    pass


class CollectiveOfferNotFound(Exception):
    pass


class UnapplicableModel(Exception):
    pass


class UnexpectedCinemaProvider(Exception):
    pass


class TiteLiveAPINotExistingEAN(Exception):
    pass


class NotUpdateProductOrOffers(Exception):
    pass


class MoveOfferBaseException(Exception):
    pass


class OfferIsNotEvent(MoveOfferBaseException):
    def __init__(self) -> None:
        super().__init__("L'offre n'est pas un évènement")


class OfferEventInThePast(MoveOfferBaseException):
    def __init__(self, count_past_stocks: int) -> None:
        super().__init__(
            f"L'évènement a déjà eu lieu pour {count_past_stocks} stock{'s' if count_past_stocks > 1 else ''}"
        )


class OfferHasReimbursedBookings(MoveOfferBaseException):
    def __init__(self, count_reimbursed_bookings: int) -> None:
        super().__init__(
            f"{count_reimbursed_bookings} {'réservations sont déjà remboursées' if count_reimbursed_bookings > 1 else 'réservation est déjà remboursée'} sur cette offre"
        )


class NoDestinationVenue(MoveOfferBaseException):
    def __init__(self) -> None:
        super().__init__(
            "Il n'existe aucun partenaire culturel avec point de valorisation vers lequel transférer l'offre"
        )


class ForbiddenDestinationVenue(MoveOfferBaseException):
    def __init__(self) -> None:
        super().__init__("Ce partenaire culturel n'est pas éligible au transfert de l'offre")


class BookingsHaveOtherPricingPoint(MoveOfferBaseException):
    def __init__(self) -> None:
        super().__init__(
            "Il existe des réservations valorisées sur un autre point de valorisation que celui du nouveau partenaire culturel"
        )


class CollectiveOfferContactRequestError(Exception):
    msg = ""
    fields = "all"


class AllNullContactRequestDataError(CollectiveOfferContactRequestError):
    msg = "All contact information are null"
    fields = "all"


class UrlandFormBothSetError(CollectiveOfferContactRequestError):
    msg = "Url and form can not both be used"
    fields = "url,form"


class InactiveOfferCanNotBeHeadline(Exception):
    def __init__(self) -> None:
        super().__init__("headlineOffer", "This offer is inactive and can not be set to the headline")


class OfferHasAlreadyAnActiveHeadlineOffer(Exception):
    def __init__(self) -> None:
        super().__init__("headlineOffer", "This offer is already an active headline offer")


class OffererCanNotHaveHeadlineOffer(Exception):
    def __init__(self) -> None:
        super().__init__("headlineOffer", "This offerer can not have headline offers")


class VirtualOfferCanNotBeHeadline(Exception):
    def __init__(self) -> None:
        super().__init__("headlineOffer", "Digital offers can not be set to the headline")


class VenueHasAlreadyAnActiveHeadlineOffer(Exception):
    def __init__(self) -> None:
        super().__init__("headlineOffer", "This venue has already an active headline offer")


class OfferWithoutImageCanNotBeHeadline(Exception):
    def __init__(self) -> None:
        super().__init__("headlineOffer", "Offers without images can not be set to the headline")


class CannotRemoveHeadlineOffer(Exception):
    def __init__(self) -> None:
        super().__init__("headlineOffer", "Error during removal of this headline offer")


class EventOpeningHoursException(Exception):
    default_field = "global"
    default_msg = "event opening hours error"

    def __init__(self, field: str, msg: str, *args: typing.Any, **kwargs: typing.Any):
        self.field = field if field else self.default_field
        self.msg = msg if msg else self.default_msg
        super().__init__(*args, **kwargs)


class CreateProductError(Exception):
    msg = "can't create this offer"


class CreateProductDBError(CreateProductError):
    msg = "internal error, can't create this offer"


class ExistingVenueWithIdAtProviderError(CreateProductDBError):
    msg = "`idAtProvider` already exists for this venue, can't create this offer"


class CreateStockError(CreateProductError):
    pass


class CreateStockDBError(CreateStockError):
    pass
