def serialize_offer_type_educational_or_individual(offer_is_educational: bool) -> str:
    return "offre scolaire" if offer_is_educational else "offre grand public"
