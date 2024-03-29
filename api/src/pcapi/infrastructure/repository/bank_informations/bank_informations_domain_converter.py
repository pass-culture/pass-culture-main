from pcapi.core.finance.models import BankInformation as BankInformationsSQLEntity
from pcapi.domain.bank_informations.bank_informations import BankInformations


def to_domain(bank_informations_sql_entity: BankInformationsSQLEntity) -> BankInformations:
    return BankInformations(
        _id=bank_informations_sql_entity.id,
        application_id=bank_informations_sql_entity.applicationId,
        status=bank_informations_sql_entity.status,
        iban=bank_informations_sql_entity.iban,
        bic=bank_informations_sql_entity.bic,
        date_modified=bank_informations_sql_entity.dateModified,
        venue_id=bank_informations_sql_entity.venueId,
    )


def to_model(bank_informations: BankInformations) -> BankInformationsSQLEntity:
    bank_informations_sql_entity = BankInformationsSQLEntity()
    bank_informations_sql_entity.id = bank_informations.id
    bank_informations_sql_entity.applicationId = bank_informations.application_id
    bank_informations_sql_entity.status = bank_informations.status
    bank_informations_sql_entity.iban = bank_informations.iban
    bank_informations_sql_entity.bic = bank_informations.bic
    bank_informations_sql_entity.offererId = bank_informations.offerer_id
    bank_informations_sql_entity.venueId = bank_informations.venue_id
    bank_informations_sql_entity.dateModified = bank_informations.date_modified

    return bank_informations_sql_entity
