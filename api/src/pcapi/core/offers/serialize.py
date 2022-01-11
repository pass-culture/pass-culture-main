def serialize_offer_type_educational_or_individual(offer_isEducational: bool) -> str:
    return "offre scolaire" if offer_isEducational else "offre grand public"
