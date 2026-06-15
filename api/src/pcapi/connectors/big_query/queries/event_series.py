import enum

from pydantic import BaseModel as BaseModelV2

from pcapi import settings
from pcapi.connectors.big_query.queries.base import BaseQuery


class DeltaAction(str, enum.Enum):
    ADD = "add"
    REMOVE = "remove"
    UPDATE = "update"


class EventSeriesModel(BaseModelV2):
    id: str
    name: str
    description: str | None = None
    mediation_uuid: str | None = None


class DeltaEventSeriesModel(EventSeriesModel):
    action: DeltaAction


class EventSeriesDeltaQuery(BaseQuery):
    raw_query = f"""
        SELECT
            event_series_id as id,
            event_series_name as name,
            event_series_description as description,
            event_series_mediation_uuid as mediation_uuid,
            action
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.event_series_delta`
        ORDER BY
        CASE action
            WHEN 'remove' THEN 1
            WHEN 'add'    THEN 2
            WHEN 'update' THEN 3
        END,
        event_series_name;
    """
    model = DeltaEventSeriesModel


class EventSeriesOfferLinkModel(BaseModelV2):
    event_series_id: str
    offer_id: int


class DeltaEventSeriesOfferLinkModel(EventSeriesOfferLinkModel):
    action: DeltaAction


class EventSeriesOfferLinkDeltaQuery(BaseQuery):
    raw_query = f"""
        SELECT
            event_series_id,
            offer_id,
            action
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.event_series_offer_link_delta`
        ORDER BY
            CASE action
            WHEN 'remove' THEN 1
            WHEN 'add'    THEN 2
        END,
        event_series_id,
        offer_id;
    """
    model = DeltaEventSeriesOfferLinkModel


class EventSeriesPreIngestionChecksModel(BaseModelV2):
    ready_for_ingestion: bool


class EventSeriesPreIngestionChecksQuery(BaseQuery):
    raw_query = f"""
        SELECT
            ready_for_ingestion
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.event_series_pre_ingestion_checks`
    """
    model = EventSeriesPreIngestionChecksModel
