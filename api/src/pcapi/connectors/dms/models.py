import datetime
import enum

import pydantic.v1 as pydantic_v1
import pytz
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class LatestDmsImport(PcObject, Base, Model):
    __tablename__ = "latest_dms_import"
    procedureId = sa.Column(sa.Integer, nullable=False)
    latestImportDatetime: datetime.datetime = sa.Column(sa.DateTime, nullable=False)
    isProcessing = sa.Column(sa.Boolean, nullable=False)
    processedApplications: list[int] = sa.Column(postgresql.ARRAY(sa.Integer), nullable=False, default=[])


def parse_dms_datetime(value: datetime.datetime | None) -> datetime.datetime | None:
    if value is None:
        return None
    return value.astimezone(pytz.utc).replace(tzinfo=None)


class DmsApplicationStates(enum.Enum):
    closed = enum.auto()
    initiated = enum.auto()
    refused = enum.auto()
    received = enum.auto()
    without_continuation = enum.auto()


class GraphQLApplicationStates(enum.Enum):
    """https://www.demarches-simplifiees.fr/graphql/schema/index.html#definition-DossierState"""

    draft = "en_construction"
    on_going = "en_instruction"
    accepted = "accepte"
    refused = "refuse"
    without_continuation = "sans_suite"


class Profile(pydantic_v1.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/profile.doc.html"""

    email: str
    id: str


class Civility(enum.Enum):
    """https://demarches-simplifiees-graphql.netlify.app/civilite.doc.html"""

    M = "M"
    MME = "Mme"


class Applicant(pydantic_v1.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/personnephysique.doc.html"""

    birth_date: datetime.date | None = pydantic_v1.Field(None, alias="dateDeNaissance")
    civility: Civility = pydantic_v1.Field(alias="civilite")
    first_name: str = pydantic_v1.Field(alias="prenom")
    id: str
    last_name: str = pydantic_v1.Field(alias="nom")
    email: str | None


class DmsField(pydantic_v1.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/champ.doc.html"""

    id: str
    label: str
    value: str | None = pydantic_v1.Field(None, alias="stringValue")
    updated_datetime: datetime.datetime | None = pydantic_v1.Field(None, alias="updatedAt")

    _format_updated_datetime = pydantic_v1.validator("updated_datetime", allow_reuse=True)(parse_dms_datetime)


class FieldLabelKeyword(enum.Enum):
    """
    Ces champs sont tirés des labels des questions des démarches DMS
    """

    ACTIVITY = "statut"
    ADDRESS = "adresse de résidence"
    BIRTH_DATE = "date de naissance"
    BIRTH_PLACE = "lieu de naissance"
    CITY_1 = "ville de résidence"
    CITY_2 = "commune de résidence"
    ID_PIECE_NUMBER = "numéro de la pièce"
    POSTAL_CODE = "code postal"
    TELEPHONE = "numéro de téléphone"


class ApplicationPageInfo(pydantic_v1.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/dossierspageinfo.doc.html"""

    end_cursor: str | None = pydantic_v1.Field(None, alias="endCursor")
    has_next_page: bool = pydantic_v1.Field(alias="hasNextPage")


class DMSMessage(pydantic_v1.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/message.doc.html"""

    created_at: datetime.datetime = pydantic_v1.Field(alias="createdAt")
    email: str

    class Config:
        allow_population_by_field_name = True

    _format_created_at = pydantic_v1.validator("created_at", allow_reuse=True)(parse_dms_datetime)


class DMSLabel(pydantic_v1.BaseModel):
    id: str
    name: str


class DemarcheDescriptor(pydantic_v1.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/demarchedescriptor.doc.html"""

    number: int


class DmsApplicationResponse(pydantic_v1.BaseModel):
    """Response from DMS API.
    https://demarches-simplifiees-graphql.netlify.app/dossier.doc.html
    """

    applicant: Applicant = pydantic_v1.Field(alias="demandeur")
    annotations: list[DmsField]
    processed_datetime: datetime.datetime | None = pydantic_v1.Field(None, alias="dateTraitement")
    draft_date: datetime.datetime = pydantic_v1.Field(alias="datePassageEnConstruction")
    fields: list[DmsField] = pydantic_v1.Field(alias="champs")
    filing_date: datetime.datetime = pydantic_v1.Field(alias="dateDepot")
    id: str
    labels: list[DMSLabel]
    latest_modification_datetime: datetime.datetime = pydantic_v1.Field(alias="dateDerniereModification")
    latest_user_fields_modification_datetime: datetime.datetime = pydantic_v1.Field(
        alias="dateDerniereModificationChamps"
    )
    messages: list[DMSMessage]
    number: int
    on_going_date: datetime.datetime | None = pydantic_v1.Field(None, alias="datePassageEnInstruction")
    procedure: DemarcheDescriptor = pydantic_v1.Field(alias="demarche")
    profile: Profile = pydantic_v1.Field(alias="usager")
    state: GraphQLApplicationStates

    _format_draft_date = pydantic_v1.validator("draft_date", allow_reuse=True)(parse_dms_datetime)
    _format_processed_datetime = pydantic_v1.validator("processed_datetime", allow_reuse=True)(parse_dms_datetime)
    _format_filing_date = pydantic_v1.validator("filing_date", allow_reuse=True)(parse_dms_datetime)
    _format_latest_modification_datetime = pydantic_v1.validator("latest_modification_datetime", allow_reuse=True)(
        parse_dms_datetime
    )
    _format_latest_user_fields_modification_datetime = pydantic_v1.validator(
        "latest_user_fields_modification_datetime", allow_reuse=True
    )(parse_dms_datetime)
    _format_on_going_date = pydantic_v1.validator("on_going_date", allow_reuse=True)(parse_dms_datetime)


class DmsPaginatedResponse(pydantic_v1.BaseModel):
    page_info: ApplicationPageInfo = pydantic_v1.Field(alias="pageInfo")


class DmsProcessApplicationsResponse(DmsPaginatedResponse):
    """Response from DMS API.
    https://demarches-simplifiees-graphql.netlify.app/demarche.doc.html
    """

    dms_applications: list[DmsApplicationResponse] = pydantic_v1.Field(alias="nodes")


class DmsDeletedApplication(pydantic_v1.BaseModel):
    """Response from DMS API.
    https://demarches-simplifiees-graphql.netlify.app/deleteddossier.doc.html
    """

    deletion_datetime: datetime.datetime = pydantic_v1.Field(alias="dateSupression")
    id: str
    number: int
    reason: str
    state: GraphQLApplicationStates

    _format_deletion_datetime = pydantic_v1.validator("deletion_datetime", allow_reuse=True)(parse_dms_datetime)


class DmsDeletedApplicationsResponse(DmsPaginatedResponse):
    dms_deleted_applications: list[DmsDeletedApplication] = pydantic_v1.Field(alias="nodes")
