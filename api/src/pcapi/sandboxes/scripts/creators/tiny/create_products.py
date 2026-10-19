from pcapi.core.categories import subcategories
from pcapi.core.offers.factories import ProductFactory


def create_tiny_products() -> None:
    ProductFactory.create(
        name="Livre du catalogue tiny",
        description="Un livre disponible dans le catalogue, sans offre associee.",
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        ean="9780000000019",
        set_all_fields=True,
    )
    ProductFactory.create(
        name="CD du catalogue tiny",
        description="Un CD disponible dans le catalogue, sans offre associee.",
        subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
        ean="2000000000022",
        set_all_fields=True,
    )
    ProductFactory.create(
        name="Vinyle du catalogue tiny",
        description="Un vinyle disponible dans le catalogue, sans offre associee.",
        subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
        ean="2000000000039",
        set_all_fields=True,
    )
