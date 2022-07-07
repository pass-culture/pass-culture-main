from pcapi.domain.client_exceptions import ClientError
from pcapi.models.api_errors import ApiErrors


class TooLateToDeleteStock(ClientError):
    def __init__(self):  # type: ignore [no-untyped-def]
        super().__init__(
            "global",
            "L'événement s'est terminé il y a plus de deux jours, la suppression est impossible.",
        )


class ImageValidationError(Exception):
    pass


class FileSizeExceeded(ImageValidationError):
    def __init__(self, max_size):  # type: ignore [no-untyped-def]
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
    def __init__(self, min_width, min_height):  # type: ignore [no-untyped-def]
        super().__init__(f"Utilisez une image plus grande (supérieure à {min_width}px par {min_height}px)")


class UnacceptedFileType(ImageValidationError):
    def __init__(self, accepted_types):  # type: ignore [no-untyped-def]
        super().__init__(f"Utilisez un format {', '.join(accepted_types)}")


class MissingImage(ImageValidationError):
    def __init__(self):  # type: ignore [no-untyped-def]
        super().__init__("Nous n'avons pas réceptionné l'image, merci d'essayer à nouveau.")


class OfferCreationBaseException(ClientError):
    pass


class SubcategoryNotEligibleForEducationalOffer(OfferCreationBaseException):
    def __init__(self):  # type: ignore [no-untyped-def]
        super().__init__(
            "offer",
            "Cette catégorie d'offre n'est pas éligible aux offres éducationnelles",
        )


class UnknownOfferSubCategory(OfferCreationBaseException):
    def __init__(self):  # type: ignore [no-untyped-def]
        super().__init__(
            "subcategory",
            "La sous-catégorie de cette offre est inconnue",
        )


class SubCategoryIsInactive(OfferCreationBaseException):
    def __init__(self):  # type: ignore [no-untyped-def]
        super().__init__(
            "subcategory",
            "Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie",
        )


class NoDelayWhenEventWithdrawalTypeHasNoTicket(OfferCreationBaseException):
    def __init__(self):  # type: ignore [no-untyped-def]
        super().__init__(
            "offer",
            "Il ne peut pas y avoir de délai de retrait lorsqu'il s'agit d'un évènement sans ticket",
        )


class EventWithTicketMustHaveDelay(OfferCreationBaseException):
    def __init__(self):  # type: ignore [no-untyped-def]
        super().__init__(
            "offer",
            "Un évènement avec ticket doit avoir un délai de renseigné",
        )


class NonWithdrawableEventOfferCantHaveWithdrawal(OfferCreationBaseException):
    def __init__(self):  # type: ignore [no-untyped-def]
        super().__init__(
            "offer",
            "Une offre qui n'a pas de ticket retirable ne peut pas avoir un type de retrait renseigné",
        )


class WithdrawableEventOfferMustHaveWithdrawal(OfferCreationBaseException):
    def __init__(self):  # type: ignore [no-untyped-def]
        super().__init__(
            "offer",
            "Une offre qui a un ticket retirable doit avoir un type de retrait renseigné",
        )


class ThumbnailStorageError(ApiErrors):
    status_code = 500


class StockDoesNotExist(ApiErrors):
    status_code = 400


class WrongFormatInFraudConfigurationFile(ApiErrors):
    pass


class OfferReportError(Exception):
    code = "OFFER_REPORT_ERROR"


class OfferAlreadyReportedError(OfferReportError):
    code = "OFFER_ALREADY_REPORTED"


class ReportMalformed(OfferReportError):
    code = "REPORT_MALFORMED"


class EducationalOfferStockBookedAndBookingNotPending(Exception):
    def __init__(self, status, booking_id):  # type: ignore [no-untyped-def]
        self.booking_status = status
        super().__init__()


class BookingLimitDatetimeTooLate(Exception):
    pass


class StockNotFound(Exception):
    pass


class OfferNotFound(Exception):
    pass


class EducationalOfferHasMultipleStocks(Exception):
    pass


class NoBookingToCancel(Exception):
    pass


class CollectiveStockNotFound(Exception):
    pass


class CollectiveOfferNotFound(Exception):
    pass


class UnapplicableModel(Exception):
    ...
