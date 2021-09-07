import pytest

from pcapi.core.categories import subcategories
from pcapi.model_creators.specific_creators import create_product_with_thing_subcategory
from pcapi.models import ApiErrors
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
def test_thing_error_when_thing_type_is_offlineOnly_but_has_url(app):
    # Given
    thing_product = create_product_with_thing_subcategory(
        thing_subcategory_id=subcategories.MATERIEL_ART_CREATIF.id, url="http://mygame.fr/offre"
    )

    # When
    with pytest.raises(ApiErrors) as errors:
        repository.save(thing_product)

    # Then
    assert errors.value.errors["url"] == [
        "Un produit de sous-catégorie MATERIEL_ART_CREATIF ne peut pas être numérique"
    ]
