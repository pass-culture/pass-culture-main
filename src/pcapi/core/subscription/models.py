import dataclasses
import datetime
from typing import Optional

import pcapi.core.fraud.models as fraud_models
from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.models.beneficiary_import import BeneficiaryImportSources


@dataclasses.dataclass
class BeneficiaryPreSubscription:
    activity: str
    address: str
    application_id: int
    city: Optional[str]
    civility: str
    date_of_birth: datetime.datetime
    email: str
    first_name: str
    id_piece_number: Optional[str]
    last_name: str
    phone_number: str
    postal_code: str
    source: str
    source_id: Optional[int]
    fraud_fields: dict

    @property
    def department_code(self) -> str:
        return PostalCode(self.postal_code).get_departement_code()

    @property
    def deposit_source(self) -> str:
        return f"dossier {self.source} [{self.application_id}]"

    @property
    def public_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def from_dms_source(cls, source_data: fraud_models.DMSContent) -> "BeneficiaryPreSubscription":
        return BeneficiaryPreSubscription(
            activity=source_data.activity,
            address=source_data.address,
            application_id=source_data.application_id,
            civility=source_data.civility,
            city=None,  # not provided in DMS applications
            date_of_birth=source_data.birth_date,
            email=source_data.email,
            first_name=source_data.first_name,
            id_piece_number=source_data.id_piece_number,
            last_name=source_data.last_name,
            phone_number=source_data.phone,
            postal_code=source_data.postal_code,
            source=BeneficiaryImportSources.demarches_simplifiees.value,
            source_id=source_data.procedure_id,
            fraud_fields={},
        )
