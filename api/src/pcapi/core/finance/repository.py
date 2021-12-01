from pcapi.core.offerers.models import Venue
from pcapi.models.bank_information import BankInformation
from pcapi.models.bank_information import BankInformationStatus

from . import models


def get_business_unit_for_offerer_id(offerer_id: str) -> list:
    return (
        models.BusinessUnit.query.join(BankInformation)
        .filter(BankInformation.status == BankInformationStatus.ACCEPTED)
        .join(Venue, models.BusinessUnit.id == Venue.businessUnitId)
        .filter(Venue.managingOffererId == offerer_id)
        .distinct(models.BusinessUnit.id)
        .with_entities(
            models.BusinessUnit.id,
            models.BusinessUnit.siret,
            models.BusinessUnit.name,
            BankInformation.iban,
            BankInformation.bic,
        )
        .all()
    )
