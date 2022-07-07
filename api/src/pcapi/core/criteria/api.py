import typing

from flask_sqlalchemy import BaseQuery
from sqlalchemy.orm import joinedload

import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.models import db

from . import models


IterIds = typing.Iterable[int]

IterOffer = typing.Iterable[offers_models.Offer]
IterVenue = typing.Iterable[offerers_models.Venue]
IterBase = IterOffer | IterVenue

Mapper = models.OfferCriterion | models.VenueCriterion

IterOfferCriterion = typing.Iterable[models.OfferCriterion]
IterVenueCriterion = typing.Iterable[models.VenueCriterion]
IterMapper = IterOfferCriterion | IterVenueCriterion

BaseModel = typing.Union[typing.Type[offers_models.Offer], typing.Type[offerers_models.Venue]]
MapperModel = typing.Union[typing.Type[models.OfferCriterion], typing.Type[models.VenueCriterion]]


class BulkUpdate:
    def __init__(self, base_ids: IterIds, criteria_ids: IterIds, replace_tags: bool = False):
        self.base_ids = base_ids
        self.criteria_ids = criteria_ids
        self.replace_tags = replace_tags

    def run(self) -> None:
        """
        Add tags to base objects (eg. Offer, Venue): for each one, find the
        missing tags and create the corresponding base_mapper_cls objects
        (eg. OfferCriterion, VenueCriterion).

        By default, this function will only add tags. To replace them
        instead, set `replace_tags` to True.
        """
        if self.replace_tags:
            self.delete_mapper_objects()

        base_objects = self.fetch_base_objects()
        missing_criteria_ids = self.compute_missing_criteria(base_objects)

        missing_offers_criteria = []
        for base_id, missing_ids in missing_criteria_ids.items():
            for criterion_id in missing_ids:
                missing_offers_criteria.append(self.build_mapper_object(base_id, criterion_id))

        db.session.bulk_save_objects(missing_offers_criteria)

    def compute_missing_criteria(self, base_objects: IterBase) -> dict[int, set[int]]:
        """
        Generic function that maps base object (eg. Offer, Venue) ids to
        missing criteria ids.
        """
        criteria_ids = set(self.criteria_ids)
        missing_base_criteria = {}

        for base_object in base_objects:
            known_criterion_ids = {crit.id for crit in base_object.criteria}
            missing_criteria_ids = criteria_ids - known_criterion_ids

            if missing_criteria_ids:
                missing_base_criteria[base_object.id] = missing_criteria_ids

        return missing_base_criteria  # type: ignore [return-value]

    def fetch_base_objects(self) -> BaseQuery:
        return self.base_cls.query.options(joinedload(self.base_cls.criteria)).filter(
            self.base_cls.id.in_(self.base_ids)  # type: ignore [union-attr]
        )

    def delete_mapper_objects(self, prefetched_criteria: bool = True) -> None:
        """
        Remove mapper objects (eg. OfferCriterion) that are linked to a
        given set of base objects' ids (eg. Offer ids).
        """
        # can't set `mapper_base_column` at a class level like
        # `mapper_cls` because of SQLA's internal behaviour/states.
        mapper_base_column = getattr(self.mapper_cls, self.mapper_base_column_name)

        # Use "fetch" option to maintain a coherent SQLA session
        self.mapper_cls.query.filter(mapper_base_column.in_(self.base_ids)).delete(synchronize_session="fetch")

    def build_mapper_object(self, base_id: int, criterion_id: int) -> Mapper:
        """
        Build a mapper object, eg. OfferCriterion
        """
        return self.mapper_cls(**{self.mapper_base_column_name: base_id, "criterionId": criterion_id})

    @property
    def base_cls(self) -> BaseModel:
        raise NotImplementedError()

    @property
    def mapper_cls(self) -> MapperModel:
        raise NotImplementedError()

    @property
    def mapper_base_column_name(self) -> str:
        raise NotImplementedError()


class OfferUpdate(BulkUpdate):
    base_cls = offers_models.Offer
    mapper_cls = models.OfferCriterion
    mapper_base_column_name = "offerId"


class VenueUpdate(BulkUpdate):
    base_cls = offerers_models.Venue
    mapper_cls = models.VenueCriterion
    mapper_base_column_name = "venueId"
