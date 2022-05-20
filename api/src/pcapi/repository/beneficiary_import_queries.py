import typing

from pcapi.models.beneficiary_import import BeneficiaryImport


def get_beneficiary_import_for_application_id_and_source_id(
    application_id: int, source_id: int
) -> typing.Optional[BeneficiaryImport]:
    return BeneficiaryImport.query.filter(
        BeneficiaryImport.applicationId == application_id, BeneficiaryImport.sourceId == source_id
    ).one_or_none()
