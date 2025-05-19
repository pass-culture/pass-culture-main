import datetime

import pytz

import pcapi.utils.date as date_utils
from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES_DICT
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db

from . import exceptions
from . import models
from . import utils


def validate_reimbursement_rule(
    rule: models.CustomReimbursementRule,
    check_start_date: bool = True,
) -> None:
    _check_reimbursement_rule_venue_has_siret(rule)
    _check_reimbursement_rule_subcategories(rule)
    _check_reimbursement_rule_dates(rule, check_start_date=check_start_date)
    _check_reimbursement_rule_conflicts(rule)


def _check_reimbursement_rule_venue_has_siret(rule: models.CustomReimbursementRule) -> None:
    if rule.venueId:
        venue = db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == rule.venueId).one()
        if not venue.siret:
            message = f"Le lieu {venue.id} - {venue.name} doit être un point de valorisation."
            raise exceptions.NotPricingPointVenueForReimbursementRule(message)


def _check_reimbursement_rule_subcategories(rule: models.CustomReimbursementRule) -> None:
    for subcategory_id in rule.subcategories:
        if subcategory_id not in ALL_SUBCATEGORIES_DICT:
            message = f""""{subcategory_id}" n'est pas une sous-catégorie valide."""
            raise exceptions.UnknownSubcategoryForReimbursementRule(message)


def _check_reimbursement_rule_dates(
    rule: models.CustomReimbursementRule,
    check_start_date: bool = True,
) -> None:
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow = date_utils.get_day_start(tomorrow, utils.ACCOUNTING_TIMEZONE)
    # If we just set the `timespan` attribute, the lower and upper
    # bounds are string objects. If `rule` was fetched from the
    # database, they are `datetime` objects. In that case, we must set
    # the timezone (to UTC, which is what we store in the database) to
    # be able to compare these objects to `tomorrow` (that has a
    # timezone).
    start_date = rule.timespan.lower
    if isinstance(start_date, str):
        start_date = datetime.datetime.fromisoformat(start_date)
    else:
        start_date = pytz.utc.localize(start_date)
    end_date = rule.timespan.upper
    if isinstance(end_date, str):
        end_date = datetime.datetime.fromisoformat(end_date)
    elif end_date is not None:
        end_date = pytz.utc.localize(end_date)

    if check_start_date and start_date < tomorrow:
        message = "Impossible d'appliquer une règle de remboursement avant le jour suivant."
        raise exceptions.WrongDateForReimbursementRule(message)
    if end_date:
        if end_date <= start_date:
            message = "La date de fin d'application doit être postérieure à la date de début."
            raise exceptions.WrongDateForReimbursementRule(message)
        if end_date < tomorrow:
            message = "La date de fin d'application ne peut pas être antérieure à demain."
            raise exceptions.WrongDateForReimbursementRule(message)


def _check_reimbursement_rule_conflicts(rule: models.CustomReimbursementRule) -> None:
    overlapping = db.session.query(models.CustomReimbursementRule)
    overlapping = overlapping.filter(models.CustomReimbursementRule.timespan.overlaps(rule.timespan))
    if rule.offerId:
        overlapping = overlapping.filter_by(offerId=rule.offerId)
    elif rule.venueId:
        overlapping = overlapping.filter_by(venueId=rule.venueId)
    else:
        overlapping = overlapping.filter_by(offererId=rule.offererId)

    # If the new rule covers all subcategories (i.e. if it does not
    # mention any specific subcategory), it conflicts with any rule
    # with an overlapping timespan.
    #
    # If the new rule covers only _some_ subcategories, it conflicts
    # only with rules with an overlapping timespan that:
    # - have at least one subcategory in common;
    # - or cover all subcategories.
    #
    # In other words, we can define rule1 on books and rule2 on shows
    # with an overlapping timespan, but that's all.
    if rule.subcategories:
        overlapping = overlapping.filter(
            (models.CustomReimbursementRule.subcategories == [])
            | models.CustomReimbursementRule.subcategories.overlap(rule.subcategories)
        )

    if rule.id:
        overlapping = overlapping.filter(models.CustomReimbursementRule.id != rule.id)
    overlapping = {str(rule_id) for (rule_id,) in overlapping.with_entities(models.CustomReimbursementRule.id)}
    if overlapping:
        raise exceptions.ConflictingReimbursementRule(
            "Cette règle est en conflit avec au moins une autre règle de remboursement.",
            conflicts=overlapping,
        )
