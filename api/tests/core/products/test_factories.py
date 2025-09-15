import pytest

from pcapi.core.categories import subcategories
from pcapi.core.categories.genres import music
from pcapi.core.offers.models import OfferExtraData
from pcapi.core.products.factories import ProductFactory
from pcapi.core.providers.titelive_gtl import GTLS


pytestmark = pytest.mark.usefixtures("db_session")


class ProductFactoryTest:
    def test_default(self):
        product = ProductFactory(set_all_fields=True)
        assert product.extraData

    def test_extradata_is_none(self):
        product = ProductFactory(extraData=None)
        assert product.extraData is None

    def test_keeps_extra_data(self):
        extra_data = OfferExtraData(author="Dan Nguyen")

        product = ProductFactory(extraData=extra_data)

        assert product.extraData == {"author": "Dan Nguyen"}

    def test_generate_cinema_extra_data(self):
        cinema_product = ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, set_all_fields=True)

        assert cinema_product.extraData is not None
        assert isinstance(cinema_product.extraData.get("author"), str)
        assert isinstance(cinema_product.extraData.get("visa"), str)
        assert isinstance(cinema_product.extraData.get("stageDirector"), str)

    def test_generate_book_extra_data(self):
        book_product = ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id, set_all_fields=True)
        import re

        assert book_product.extraData is not None
        assert isinstance(book_product.extraData.get("author"), str)
        assert re.match(r"\d{13}", book_product.ean)
        assert book_product.extraData.get("gtl_id") in GTLS

    def test_generate_CDs_extra_data(self):
        concert_product = ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id, set_all_fields=True
        )

        assert concert_product.extraData is not None
        assert isinstance(concert_product.extraData.get("author"), str)
        assert isinstance(concert_product.extraData.get("performer"), str)

        music_type_code = int(concert_product.extraData.get("musicType"))
        music_type = music.MUSIC_TYPES_BY_CODE.get(music_type_code)
        assert music_type_code in music.MUSIC_TYPES_BY_CODE

        music_sub_type_code = int(concert_product.extraData.get("musicSubType"))
        music_sub_type = music.MUSIC_SUB_TYPES_BY_CODE.get(music_sub_type_code)

        assert music_sub_type_code == -1 or music_sub_type in music_type.children

    def test_generate_vinyles_extra_data(self):
        concert_product = ProductFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id, set_all_fields=True
        )

        assert concert_product.extraData is not None
        assert isinstance(concert_product.extraData.get("author"), str)
        assert isinstance(concert_product.extraData.get("performer"), str)

        music_type_code = int(concert_product.extraData.get("musicType"))
        music_type = music.MUSIC_TYPES_BY_CODE.get(music_type_code)
        assert music_type_code in music.MUSIC_TYPES_BY_CODE

        music_sub_type_code = int(concert_product.extraData.get("musicSubType"))
        music_sub_type = music.MUSIC_SUB_TYPES_BY_CODE.get(music_sub_type_code)

        assert music_sub_type_code == -1 or music_sub_type in music_type.children
