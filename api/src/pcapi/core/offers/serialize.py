import enum


def serialize_offer_type_educational_or_individual(offer_is_educational: bool) -> str:
    return "offre collective" if offer_is_educational else "offre grand public"


class CollectiveOfferType(enum.Enum):
    offer = "offer"
    template = "template"
