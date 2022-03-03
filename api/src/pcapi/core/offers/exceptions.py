import humanize

from pcapi.domain.client_exceptions import ClientError
from pcapi.models.api_errors import ApiErrors


class TooLateToDeleteStock(ClientError):
    def __init__(self):
        super().__init__(
            "global",
            "L'événement s'est terminé il y a plus de deux jours, la suppression est impossible.",
        )


class ImageValidationError(Exception):
    pass


class FileSizeExceeded(ImageValidationError):
    def __init__(self, max_size):
        super().__init__(f"Utilisez une image dont le poids est inférieur à {humanize.naturalsize(max_size)}")


class ImageTooSmall(ImageValidationError):
    def __init__(self, min_width, min_height):
        super().__init__(f"Utilisez une image plus grande (supérieure à {min_width}px par {min_height}px)")


class UnacceptedFileType(ImageValidationError):
    def __init__(self, accepted_types):
        super().__init__(f"Utilisez un format {', '.join(accepted_types)}")


class MissingImage(ImageValidationError):
    def __init__(self):
        super().__init__("Nous n'avons pas réceptionné l'image, merci d'essayer à nouveau.")


class SubcategoryNotEligibleForEducationalOffer(ClientError):
    def __init__(self):
        super().__init__(
            "offer",
            "Cette catégorie d'offre n'est pas éligible aux offres éducationnelles",
        )


class UnknownOfferSubCategory(ClientError):
    def __init__(self):
        super().__init__(
            "subcategory",
            "La sous-catégorie de cette offre est inconnue",
        )


class SubCategoryIsInactive(ClientError):
    def __init__(self):
        super().__init__(
            "subcategory",
            "Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie",
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
    def __init__(self, status, booking_id):
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
