from dataclasses import dataclass


@dataclass(frozen=True)
class OffererTagCategory:
    id: str
    label: str


# Partners counting projects, for data analytics to apply different rules on offerers
COMPTAGE = OffererTagCategory(id="COMPTAGE", label="Comptage Partenaires")

# Tags used for filtering offerers to validate
HOMOLOGATION = OffererTagCategory(id="HOMOLOGATION", label="Homologation")

ALL_OFFERER_TAG_CATEGORIES = (
    COMPTAGE,
    HOMOLOGATION,
)

ALL_OFFERER_TAG_CATEGORIES_DICT = {subcategory.id: subcategory for subcategory in ALL_OFFERER_TAG_CATEGORIES}
