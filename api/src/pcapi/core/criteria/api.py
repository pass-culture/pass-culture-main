import sqlalchemy.exc as sa_exc

import pcapi.core.criteria.models as criteria_models
import pcapi.core.offerers.models as offerers_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


def get_or_create_category(label: str) -> criteria_models.CriterionCategory:
    result = (
        db.session.query(criteria_models.CriterionCategory)
        .filter(criteria_models.CriterionCategory.label == label)
        .one_or_none()
    )
    if not result:
        result = criteria_models.CriterionCategory(label=label)
        db.session.add(result)
    return result


def get_or_create_criteria(
    name: str, description: str | None = None, category_labels: list[str] | None = None
) -> criteria_models.Criterion:
    result = db.session.query(criteria_models.Criterion).filter(criteria_models.Criterion.name == name).one_or_none()
    if not result:
        categories = None
        if category_labels:
            categories = [get_or_create_category(category_label) for category_label in category_labels]
        result = criteria_models.Criterion(name=name, description=description, categories=categories)
        db.session.add(result)
    return result


def link_criterion_to_venue(criterion: criteria_models.Criterion, venue: offerers_models.Venue) -> None:
    try:
        with atomic():
            link = criteria_models.VenueCriterion(criterionId=criterion.id, venueId=venue.id)
            db.session.add(link)
            db.session.flush([link])
    except sa_exc.IntegrityError:
        pass
