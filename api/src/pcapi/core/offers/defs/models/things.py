import typing
from typing import Literal

import pydantic as pydantic_v2

from . import shared
from .base import Base
from .base import Typology


class AboBibliothequeModel(Base):
    subcategory_id: Literal["ABO_BIBLIOTHEQUE"]
    typology: Literal[Typology.THINGS] = Typology.THINGS


class AboConcertModel(Base):
    subcategory_id: Literal["ABO_CONCERT"]
    extra_data: shared.ExtraDataConcert
    typology: Literal[Typology.THINGS] = Typology.THINGS


class AboMediathequeModel(Base):
    subcategory_id: Literal["ABO_MEDIATHEQUE"]
    typology: Literal[Typology.THINGS] = Typology.THINGS


class AboPratiqueArtModel(Base):
    subcategory_id: Literal["ABO_PRATIQUE_ART"]
    typology: Literal[Typology.THINGS] = Typology.THINGS


class AchatInstrumentModel(Base):
    subcategory_id: Literal["ACHAT_INSTRUMENT"]
    extra_data: shared.ExtraDataEan
    typology: Literal[Typology.THINGS] = Typology.THINGS


class CarteCineIllimiteModel(Base):
    subcategory_id: Literal["CARTE_CINE_ILLIMITE"]
    typology: Literal[Typology.THINGS] = Typology.THINGS


class CarteCineUultiseancesModel(Base):
    subcategory_id: Literal["CARTE_CINE_MULTISEANCES"]
    typology: Literal[Typology.THINGS] = Typology.THINGS


class CarteJeunesModel(Base):
    subcategory_id: Literal["CARTE_JEUNES"]
    typology: Literal[Typology.THINGS] = Typology.THINGS


class CarteMuseeModel(Base):
    subcategory_id: Literal["CARTE_MUSEE"]
    typology: Literal[Typology.THINGS] = Typology.THINGS


class EscapeGameModel(Base):
    subcategory_id: Literal["ESCAPE_GAME"]
    typology: Literal[Typology.THINGS] = Typology.THINGS


class LivreAudioPhysiqueModel(Base):
    subcategory_id: Literal["LIVRE_AUDIO_PHYSIQUE"]
    extra_data: shared.ExtraDataBook
    typology: Literal[Typology.THINGS] = Typology.THINGS


class LocationInstrumentModel(Base):
    subcategory_id: Literal["LOCATION_INSTRUMENT"]
    extra_data: shared.ExtraDataEan
    typology: Literal[Typology.THINGS] = Typology.THINGS


class MaterielArtCreatifModel(Base):
    subcategory_id: Literal["MATERIEL_ART_CREATIF"]
    extra_data: shared.ExtraDataEan
    typology: Literal[Typology.THINGS] = Typology.THINGS


class PartitionModel(Base):
    subcategory_id: Literal["PARTITION"]
    extra_data: shared.ExtraDataEan
    typology: Literal[Typology.THINGS] = Typology.THINGS


class SupportPhysiqueFilmModel(Base):
    subcategory_id: Literal["SUPPORT_PHYSIQUE_FILM"]
    extra_data: shared.ExtraDataEan
    typology: Literal[Typology.THINGS] = Typology.THINGS


class LivrePapierModel(Base):
    product: shared.Product | None = None
    provider_data: shared.ProviderData | None = None
    subcategory_id: Literal["LIVRE_PAPIER"]
    extra_data: shared.ExtraDataBookWithGtl
    typology: Literal[Typology.THINGS] = Typology.THINGS


class SupportPhysiqueMusiqueVinyleModel(Base):
    product: shared.Product | None = None
    provider_data: shared.ProviderData | None = None
    subcategory_id: Literal["SUPPORT_PHYSIQUE_MUSIQUE_VINYLE"]
    extra_data: shared.ExtraDataMusicWithEan
    typology: Literal[Typology.THINGS] = Typology.THINGS


class SupportPhysiqueMusiqueCDModel(Base):
    product: shared.Product | None = None
    provider_data: shared.ProviderData | None = None
    subcategory_id: Literal["SUPPORT_PHYSIQUE_MUSIQUE_CD"]
    venue: shared.Venue
    extra_data: shared.ExtraDataMusicWithEan
    typology: Literal[Typology.THINGS] = Typology.THINGS

    @pydantic_v2.model_validator(mode="after")
    def check_has_product_if_from_record_store(self) -> typing.Self:
        if self.venue.code == shared.VenueTypeCode.RECORD_STORE and not self.product:
            raise ValueError("Record store implies that a product is set")
        return self
