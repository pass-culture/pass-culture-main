import typing
from typing import Literal

import pydantic as pydantic_v2

from . import shared
from .base import Base


class AboBibliothequeModel(Base):
    subcategory_id: Literal["ABO_BIBLIOTHEQUE"]


class AboConcertModel(Base):
    subcategory_id: Literal["ABO_CONCERT"]
    extra_data: shared.ExtraDataConcert


class AboMediathequeModel(Base):
    subcategory_id: Literal["ABO_MEDIATHEQUE"]


class AboPratiqueArtModel(Base):
    subcategory_id: Literal["ABO_PRATIQUE_ART"]


class AchatInstrumentModel(Base):
    subcategory_id: Literal["ACHAT_INSTRUMENT"]
    extra_data: shared.ExtraDataEan


class CarteCineIllimiteModel(Base):
    subcategory_id: Literal["CARTE_CINE_ILLIMITE"]


class CarteCineUultiseancesModel(Base):
    subcategory_id: Literal["CARTE_CINE_MULTISEANCES"]


class CarteJeunesModel(Base):
    subcategory_id: Literal["CARTE_JEUNES"]


class CarteMuseeModel(Base):
    subcategory_id: Literal["CARTE_MUSEE"]


class EscapeGameModel(Base):
    subcategory_id: Literal["ESCAPE_GAME"]


class LivreAudioPhysiqueModel(Base):
    subcategory_id: Literal["LIVRE_AUDIO_PHYSIQUE"]
    extra_data: shared.ExtraDataBook


class LocationInstrumentModel(Base):
    subcategory_id: Literal["LOCATION_INSTRUMENT"]
    extra_data: shared.ExtraDataEan


class MaterielArtCreatifModel(Base):
    subcategory_id: Literal["MATERIEL_ART_CREATIF"]
    extra_data: shared.ExtraDataEan


class PartitionModel(Base):
    subcategory_id: Literal["PARTITION"]
    extra_data: shared.ExtraDataEan


class SupportPhysiqueFilmModel(Base):
    subcategory_id: Literal["SUPPORT_PHYSIQUE_FILM"]
    extra_data: shared.ExtraDataEan


class Product(pydantic_v2.BaseModel):
    id: int


class ProviderData(pydantic_v2.BaseModel):
    id_at_provider: str
    provider_id: int


class LivrePapierModel(Base):
    product: Product | None = None
    provider_data: ProviderData | None = None
    subcategory_id: Literal["LIVRE_PAPIER"]
    extra_data: shared.ExtraDataBookWithGtl


class SupportPhysiqueMusiqueVinyleModel(Base):
    product: Product | None = None
    provider_data: ProviderData | None = None
    subcategory_id: Literal["SUPPORT_PHYSIQUE_MUSIQUE_VINYLE"]
    extra_data: shared.ExtraDataMusicWithEan


class SupportPhysiqueMusiqueCDModel(Base):
    product: Product | None = None
    provider_data: ProviderData | None = None
    subcategory_id: Literal["SUPPORT_PHYSIQUE_MUSIQUE_CD"]
    venue: shared.Venue
    extra_data: shared.ExtraDataMusicWithEan

    @pydantic_v2.model_validator(mode="after")
    def check_has_product_if_from_record_store(self) -> typing.Self:
        if self.venue.code == shared.VenueTypeCode.RECORD_STORE and not self.product:
            raise ValueError("Record store implies that a product is set")
        return self
