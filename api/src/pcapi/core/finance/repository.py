import datetime

import pytz

import pcapi.core.offerers.models as offerers_models
import pcapi.core.payments.utils as payments_utils
from pcapi.models.bank_information import BankInformation
from pcapi.models.bank_information import BankInformationStatus
import pcapi.utils.date as date_utils

from . import models


def get_business_units_for_offerer_id(offerer_id: str) -> list:
    return (
        models.BusinessUnit.query.join(BankInformation)
        .filter(BankInformation.status == BankInformationStatus.ACCEPTED)
        .join(offerers_models.Venue, models.BusinessUnit.id == offerers_models.Venue.businessUnitId)
        .filter(offerers_models.Venue.managingOffererId == offerer_id)
        .distinct(models.BusinessUnit.id)
        .with_entities(
            models.BusinessUnit.id, models.BusinessUnit.siret, models.BusinessUnit.name, BankInformation.iban
        )
        .all()
    )


def get_invoices_query(
    offerer_id,
    business_unit_id: int = None,
    date_from: datetime.date = None,
    date_until: datetime.date = None,
):
    """Return invoices for the requested offerer.

    If given, ``date_from`` is **inclusive**, ``date_until`` is
    **exclusive**.
    """
    business_units_subquery = offerers_models.Venue.query.filter_by(managingOffererId=offerer_id).with_entities(
        offerers_models.Venue.businessUnitId
    )
    if business_unit_id:
        # Filtering like this makes sure that the requested business
        # unit id belongs to the offerer.
        business_units_subquery = business_units_subquery.filter(
            offerers_models.Venue.businessUnitId == business_unit_id
        )
    invoices = models.Invoice.query.filter(models.Invoice.businessUnitId.in_(business_units_subquery.subquery()))
    convert_to_datetime = lambda date: date_utils.get_day_start(date, payments_utils.ACCOUNTING_TIMEZONE).astimezone(
        pytz.utc
    )
    if date_from:
        datetime_from = convert_to_datetime(date_from)
        invoices = invoices.filter(models.Invoice.date >= datetime_from)
    if date_until:
        datetime_until = convert_to_datetime(date_until)
        invoices = invoices.filter(models.Invoice.date < datetime_until)

    return invoices
