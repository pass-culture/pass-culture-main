import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.models import OfferExtraData
from pcapi.domain import music_types
from pcapi.domain import show_types


pytestmark = pytest.mark.usefixtures("db_session")


class OfferFactoryTest:
    def test_default(self):
        offer = OfferFactory(set_all_fields=True)
        assert offer.extraData

    def test_extradata_is_none(self):
        offer = OfferFactory(extraData=None)
        assert offer.extraData is None

    def test_keeps_extra_data(self):
        extra_data = OfferExtraData(author="Dan Nguyen")

        offer = OfferFactory(extraData=extra_data)

        assert offer.extraData == {"author": "Dan Nguyen"}

    def test_generate_book_extra_data_does_not_set_gtl_id(self):
        book_offer = OfferFactory(subcategoryId=subcategories.LIVRE_PAPIER.id, set_all_fields=True)
        assert book_offer.extraData.get("gtl_id") is None

    def test_generate_cinema_extra_data(self):
        cinema_offer = OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id, set_all_fields=True)

        assert cinema_offer.extraData is not None
        assert isinstance(cinema_offer.extraData.get("author"), str)
        assert isinstance(cinema_offer.extraData.get("visa"), str)
        assert isinstance(cinema_offer.extraData.get("stageDirector"), str)

    def test_generate_book_extra_data(self):
        book_offer = OfferFactory(subcategoryId=subcategories.LIVRE_PAPIER.id, set_all_fields=True)
        import re

        assert book_offer.extraData is not None
        assert isinstance(book_offer.extraData.get("author"), str)
        assert re.match(r"\d{13}", book_offer.extraData.get("ean"))

    def test_generate_concert_extra_data(self):
        concert_offer = OfferFactory(subcategoryId=subcategories.CONCERT.id, set_all_fields=True)

        assert concert_offer.extraData is not None
        assert isinstance(concert_offer.extraData.get("author"), str)
        assert isinstance(concert_offer.extraData.get("performer"), str)

        music_type_code = int(concert_offer.extraData.get("musicType"))
        music_type = music_types.MUSIC_TYPES_BY_CODE.get(music_type_code)
        assert music_type_code in music_types.MUSIC_TYPES_BY_CODE

        music_sub_type_code = int(concert_offer.extraData.get("musicSubType"))
        music_sub_type = music_types.MUSIC_SUB_TYPES_BY_CODE.get(music_sub_type_code)

        assert music_sub_type_code == -1 or music_sub_type in music_type.children

    def test_generate_spectacle_representation_extra_data(self):
        concert_offer = OfferFactory(subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id, set_all_fields=True)

        assert concert_offer.extraData is not None
        assert isinstance(concert_offer.extraData.get("author"), str)
        assert isinstance(concert_offer.extraData.get("stageDirector"), str)
        assert isinstance(concert_offer.extraData.get("performer"), str)

        show_type_code = int(concert_offer.extraData.get("showType"))
        show_type = show_types.SHOW_TYPES_BY_CODE.get(show_type_code)
        assert show_type_code in show_types.SHOW_TYPES_BY_CODE

        show_sub_type_code = int(concert_offer.extraData.get("showSubType"))
        show_sub_type = show_types.SHOW_SUB_TYPES_BY_CODE.get(show_sub_type_code)

        assert show_sub_type_code == -1 or show_sub_type in show_type.children
