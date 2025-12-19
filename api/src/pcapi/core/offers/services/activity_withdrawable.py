from typing import Annotated
from typing import Literal

import pydantic as pydantic_v2

from pcapi.core.categories import subcategories
from pcapi.core.offers import models

from . import shared
from .activity import ActivityBaseModel


class SpectacleExtraData(pydantic_v2.BaseModel):
    showType: shared.ShowType
    showSubType: shared.ShowSubType
    performer: Annotated[str, shared.NameString] | None = None
    stageDirector: Annotated[str, shared.NameString] | None = None
    author: Annotated[str, shared.NameString] | None = None


class ArtVisuelExtraData(pydantic_v2.BaseModel):
    performer: Annotated[str, shared.NameString] | None = None
    author: Annotated[str, shared.NameString] | None = None


class MusiqueExtraData(pydantic_v2.BaseModel):
    # WARNING(jbaudet - 12/2025): `music_type` seems to be mandatory
    # when creating from the public API and not when its from the
    # PRO routes. Why?...
    music_type: shared.MusicType | None = None
    music_sub_type: shared.MusicSubType | None = None
    performer: Annotated[str, shared.NameString] | None = None
    author: Annotated[str, shared.NameString] | None = None
    gtl_id: Annotated[str, shared.GtlIdString] | None = None


class NoTicketWithdrawal(pydantic_v2.BaseModel):
    withdrawal_type: Literal[models.WithdrawalTypeEnum.NO_TICKET.value]
    withdrawal_delay: None = None
    has_ticketing_service: bool | None = None


class OnSiteWithdrawal(pydantic_v2.BaseModel):
    withdrawal_type: Literal[models.WithdrawalTypeEnum.ON_SITE.value]
    withdrawal_delay: int
    has_ticketing_service: bool | None = None


class EmailWithdrawal(pydantic_v2.BaseModel):
    withdrawal_type: Literal[models.WithdrawalTypeEnum.BY_EMAIL.value]
    withdrawal_delay: int
    has_ticketing_service: bool | None = None


class InAppWithdrawal(pydantic_v2.BaseModel):
    withdrawal_type: Literal[models.WithdrawalTypeEnum.IN_APP.value]
    withdrawal_delay: None = None
    has_ticketing_service: Literal[True]


WithdrawalInfo = NoTicketWithdrawal | OnSiteWithdrawal | EmailWithdrawal | InAppWithdrawal


class ActivityWithTicketBaseModel(ActivityBaseModel):
    withdrawal: WithdrawalInfo


class SpectacleRepresentationModel(ActivityWithTicketBaseModel):
    subcategory_id: Literal[subcategories.SPECTACLE_REPRESENTATION.id]
    extra_data: SpectacleExtraData


class FestivalSpectacleModel(ActivityWithTicketBaseModel):
    subcategory_id: Literal[subcategories.FESTIVAL_SPECTACLE.id]
    extra_data: SpectacleExtraData


class FestivalArtVisuelModel(ActivityWithTicketBaseModel):
    subcategory_id: Literal[subcategories.FESTIVAL_ART_VISUEL.id]
    extra_data: ArtVisuelExtraData


class ConcertModel(ActivityWithTicketBaseModel):
    subcategory_id: Literal[subcategories.CONCERT.id]
    extra_data: MusiqueExtraData


class FestivalMusiqueModel(ActivityWithTicketBaseModel):
    subcategory_id: Literal[subcategories.FESTIVAL_MUSIQUE.id]
    extra_data: MusiqueExtraData


class EvenementMusiqueModel(ActivityWithTicketBaseModel):
    subcategory_id: Literal[subcategories.EVENEMENT_MUSIQUE.id]
    extra_data: MusiqueExtraData
