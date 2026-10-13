import typing
from datetime import date
from datetime import datetime

from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator

from pcapi.core.discoveries import models
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


class CreateDiscoverySchema(HttpBodyModel):
    work_id: int | None = Field(default=None, gt=0, le=2**63 - 1)
    artist_id: str | None = Field(default=None, min_length=1)
    offer_id: int | None = Field(default=None, gt=0, le=2**63 - 1)
    discovery_date: date | None = None
    format_context: str | None = None
    comment: str | None = None
    emotions: list[models.DiscoveryEmotion] | None = None

    @model_validator(mode="after")
    def validate_exactly_one_target(self) -> typing.Self:
        if sum(target is not None for target in (self.work_id, self.artist_id, self.offer_id)) != 1:
            raise ValueError("Exactly one of work_id, artist_id or offer_id is required")
        return self


class UpdateDiscoverySchema(HttpBodyModel):
    discovery_date: date | None = None
    comment: str | None = None
    emotions: list[models.DiscoveryEmotion] | None = None

    @field_validator("discovery_date")
    @classmethod
    def validate_discovery_date(cls, value: date | None) -> date:
        if value is None:
            raise ValueError("discovery_date cannot be null")
        return value


class DiscoveriesQuerySchema(HttpQueryParamsModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class ArtistResponseSchema(HttpBodyModel):
    id: str
    name: str
    main_role: str | None


class WorkResponseSchema(HttpBodyModel):
    id: int
    title: str
    media_type: models.WorkMediaType
    release_year: int | None
    visual_url: str | None
    main_artist: ArtistResponseSchema | None = None

    @classmethod
    def build(cls, work: models.Work) -> typing.Self:
        main_role = {
            models.WorkMediaType.BOOK: "author",
            models.WorkMediaType.FILM: "film_director",
            models.WorkMediaType.MUSIC: "performer",
            models.WorkMediaType.PERFORMING_ART: "stage_director",
        }.get(work.media_type)
        main_link = next(
            (link for link in sorted(work.artist_links, key=lambda link: link.artist_id) if link.role == main_role),
            None,
        )
        response = cls.model_validate(work)
        if main_link is not None:
            response.main_artist = ArtistResponseSchema.model_validate(main_link.artist)
        return response


class DiscoveryResponseSchema(HttpBodyModel):
    id: int
    work_id: int | None
    artist_id: str | None
    offer_origin_id: int | None
    discovery_date: date
    format_context: str | None
    comment: str | None
    emotions: list[models.DiscoveryEmotion] | None
    created_at: datetime
    work: WorkResponseSchema | None
    artist: ArtistResponseSchema | None

    @classmethod
    def build(cls, discovery: models.Discovery) -> typing.Self:
        return cls(
            id=discovery.id,
            work_id=discovery.work_id,
            artist_id=discovery.artist_id,
            offer_origin_id=discovery.offer_origin_id,
            discovery_date=discovery.discovery_date,
            format_context=discovery.format_context,
            comment=discovery.comment,
            emotions=discovery.emotions,
            created_at=discovery.created_at,
            work=WorkResponseSchema.build(discovery.work) if discovery.work else None,
            artist=ArtistResponseSchema.model_validate(discovery.artist) if discovery.artist else None,
        )


class DiscoveriesResponseSchema(HttpBodyModel):
    page: int
    limit: int
    discoveries: list[DiscoveryResponseSchema]
