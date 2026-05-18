import pydantic as pydantic_v2

from . import constrained_types


class ExtraData(pydantic_v2.BaseModel):
    model_config = pydantic_v2.ConfigDict(extra="forbid")


class ExtraDataEan(ExtraData):
    ean: constrained_types.EanString | None = None


class ExtraDataShow(ExtraData):
    show_type: constrained_types.ShowType
    show_sub_type: constrained_types.ShowSubType


class ExtraDataEvent(ExtraData):
    show_type: constrained_types.ShowType
    show_sub_type: constrained_types.ShowSubType
    author: constrained_types.NameString | None = None
    performer: constrained_types.NameString | None = None
    stage_director: constrained_types.NameString | None = None


class ExtraDataArtistic(ExtraData):
    show_type: constrained_types.ShowType
    show_sub_type: constrained_types.ShowSubType
    music_type: constrained_types.MusicType
    music_sub_type: constrained_types.MusicSubType
    gtl_id: constrained_types.TiteliveMusicGenres


class ExtraDataMusic(ExtraData):
    performer: constrained_types.NameString | None = None
    author: constrained_types.NameString | None = None
    music_type: constrained_types.MusicType | None = None
    music_sub_type: constrained_types.MusicSubType | None = None
    gtl_id: constrained_types.TiteliveMusicGenres | None = None


class ExtraDataMusicWithEan(ExtraData):
    performer: constrained_types.NameString | None = None
    author: constrained_types.NameString | None = None
    music_type: constrained_types.MusicType | None = None
    music_sub_type: constrained_types.MusicSubType | None = None
    gtl_id: constrained_types.TiteliveMusicGenres | None = None
    ean: constrained_types.EanString | None = None


class ExtraDataConcert(ExtraData):
    music_type: constrained_types.MusicType | None = None
    gtl_id: constrained_types.TiteliveMusicGenres | None = None


class ExtraDataPerformance(ExtraData):
    show_type: constrained_types.ShowType
    show_sub_type: constrained_types.ShowSubType
    performer: constrained_types.NameString | None = None
    stage_director: constrained_types.NameString | None = None
    author: constrained_types.NameString | None = None


# NOTE(jbaudet): should at least the author be set? the visa?
class ExtraDataCinema(ExtraData):
    visa: constrained_types.VisaString | None = None
    stage_director: constrained_types.NameString | None = None
    author: constrained_types.NameString | None = None


class ExtraDataSpeaker(ExtraData):
    speaker: constrained_types.NameString | None = None


class ExtraDataAuthor(ExtraData):
    author: constrained_types.NameString | None = None


class ExtraDataBook(ExtraData):
    ean: constrained_types.EanString | None = None
    author: constrained_types.NameString | None = None


class ExtraDataBookWithGtl(ExtraData):
    ean: constrained_types.EanString | None = None
    author: constrained_types.NameString | None = None
    gtl_id: constrained_types.GtlIdString | None = None


class ExtraDataVisualArt(ExtraData):
    performer: constrained_types.NameString | None = None
    author: constrained_types.NameString | None = None
