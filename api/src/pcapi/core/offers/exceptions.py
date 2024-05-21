import typing

from pcapi.domain.client_exceptions import ClientError
from pcapi.models.api_errors import ApiErrors


class TooLateToDeleteStock(ClientError):
    def __init__(self) -> None:
        super().__init__(
            "global",
            "L'évènement s'est terminé il y a plus de deux jours, la suppression est impossible.",
        )


class OfferUsedOrReimbursedCantBeEdit(Exception):
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
    def __init__(self, min_width: int, min_height: int) -> None:
        super().__init__(f"Utilisez une image plus grande (supérieure à {min_width}px par {min_height}px)")


class ImageTooLarge(ImageValidationError):
    def __init__(self, max_width: int | None, max_height: int | None):
        if max_width and not max_height:
            super().__init__(f"Utilisez une image plus petite (inférieure à {max_width} px de large)")
        elif max_height and not max_width:
            super().__init__(f"Utilisez une image plus petite (inférieure à  {max_height}px de haut)")
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


class OfferCreationBaseException(ClientError):
    pass


class OfferCannotBeDuo(OfferCreationBaseException):
    def __init__(self) -> None:
        super().__init__("enableDoubleBookings", "the category chosen does not allow double bookings")


class SubcategoryNotEligibleForEducationalOffer(OfferCreationBaseException):
    def __init__(self) -> None:
        super().__init__(
            "offer",
            "Cette catégorie d'offre n'est pas éligible aux offres éducationnelles",
        )


class UnknownOfferSubCategory(OfferCreationBaseException):
    def __init__(self) -> None:
        super().__init__(
            "subcategory",
            "La sous-catégorie de cette offre est inconnue",
        )


class SubCategoryIsInactive(OfferCreationBaseException):
    def __init__(self) -> None:
        super().__init__(
            "subcategory",
            "Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie",
        )


class CannotSetIdAtProviderWithoutAProvider(OfferCreationBaseException):
    def __init__(self) -> None:
        super().__init__(
            "idAtProvider",
            "Une offre ne peut être créée ou éditée avec un idAtProvider si elle n'a pas de provider",
        )


class NoDelayWhenEventWithdrawalTypeHasNoTicket(OfferCreationBaseException):
    def __init__(self) -> None:
        super().__init__(
            "offer",
            "Il ne peut pas y avoir de délai de retrait lorsqu'il s'agit d'un évènement sans ticket",
        )


class EventWithTicketMustHaveDelay(OfferCreationBaseException):
    def __init__(self) -> None:
        super().__init__(
            "offer",
            "Un évènement avec ticket doit avoir un délai de renseigné",
        )


class NonLinkedProviderCannotHaveInAppTicket(OfferCreationBaseException):
    def __init__(self) -> None:
        super().__init__(
            "offer",
            "Vous devez supporter l'interface de billeterie pour créer des offres avec billet",
        )


class WithdrawableEventOfferMustHaveWithdrawal(OfferCreationBaseException):
    def __init__(self) -> None:
        super().__init__(
            "offer",
            "Une offre qui a un ticket retirable doit avoir un type de retrait renseigné",
        )


class WithdrawableEventOfferMustHaveBookingContact(OfferCreationBaseException):
    def __init__(self) -> None:
        super().__init__(
            "offer",
            "Une offre qui a un ticket retirable doit avoir l'email du contact de réservation",
        )


class ExtraDataValueNotAllowed(OfferCreationBaseException):
    pass


class OfferAlreadyExists(OfferCreationBaseException):
    def __init__(self, field: str) -> None:
        super().__init__(
            field, f"Une offre avec cet {field.upper()} existe déjà. Vous pouvez la retrouver dans l’onglet Offres."
        )


class EanFormatException(OfferCreationBaseException):
    pass


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


class BookingLimitDatetimeTooLate(OfferCreationBaseException):
    def __init__(self) -> None:
        super().__init__(
            "bookingLimitDatetime",
            "The bookingLimitDatetime must be before the beginning of the event",
        )


class OfferNotFound(Exception):
    pass


class ProductNotFound(Exception):
    pass


class CollectiveStockNotFound(Exception):
    pass


class CollectiveOfferNotFound(Exception):
    pass


class UnapplicableModel(Exception): ...


class UnexpectedCinemaProvider(Exception):
    pass


class TiteLiveAPINotExistingEAN(Exception):
    pass


class NotUpdateProductOrOffers(Exception):
    pass


class OfferEditionBaseException(ClientError):
    pass


class RejectedOrPendingOfferNotEditable(OfferEditionBaseException):
    def __init__(self) -> None:
        super().__init__("global", "Les offres refusées ou en attente de validation ne sont pas modifiables")


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
        super().__init__("Il n'existe aucun lieu avec point de valorisation vers lequel transférer l'offre")


class ForbiddenDestinationVenue(MoveOfferBaseException):
    def __init__(self) -> None:
        super().__init__("Ce lieu n'est pas éligible au transfert de l'offre")


class BookingsHaveOtherPricingPoint(MoveOfferBaseException):
    def __init__(self) -> None:
        super().__init__(
            "Il existe des réservations valorisées sur un autre point de valorisation que celui du nouveau lieu"
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
