import datetime
import enum
import typing

import pydantic
import pytz
import sqlalchemy as sa
from sqlalchemy import orm as sa_orm
from sqlalchemy.dialects import postgresql

from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class LatestDmsImport(PcObject, Model):
    __tablename__ = "latest_dms_import"
    procedureId = sa_orm.mapped_column(sa.Integer, nullable=False)
    latestImportDatetime: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(sa.DateTime, nullable=False)
    isProcessing = sa_orm.mapped_column(sa.Boolean, nullable=False)
    processedApplications: sa_orm.Mapped[list[int]] = sa_orm.mapped_column(
        postgresql.ARRAY(sa.Integer), nullable=False, default=[]
    )


def to_naive_utc(value: datetime.datetime | None) -> datetime.datetime | None:
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


class Profile(pydantic.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/profile.doc.html"""

    email: str
    id: str


class Civility(enum.Enum):
    """https://demarches-simplifiees-graphql.netlify.app/civilite.doc.html"""

    M = "M"
    MME = "Mme"


class Applicant(pydantic.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/personnephysique.doc.html"""

    birth_date: datetime.date | None = pydantic.Field(None, alias="dateDeNaissance")
    civility: Civility = pydantic.Field(alias="civilite")
    first_name: str = pydantic.Field(alias="prenom")
    id: str
    last_name: str = pydantic.Field(alias="nom")
    email: str | None = None


DmsDatetime = typing.Annotated[datetime.datetime, pydantic.AfterValidator(to_naive_utc)]


class DmsField(pydantic.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/champ.doc.html"""

    id: str
    label: str
    value: str | None = pydantic.Field(None, alias="stringValue")
    updated_datetime: DmsDatetime | None = pydantic.Field(None, alias="updatedAt")


class FieldLabelKeyword(enum.Enum):
    """
    Ces champs sont tirés des labels des questions des démarches DMS
    """

    ACTIVITY = "statut"
    ADDRESS = "adresse de résidence"
    BIRTH_CITY = "ville de naissance"
    BIRTH_DATE = "date de naissance"
    BIRTH_PLACE = "lieu de naissance"  # now BIRTH_CITY, but kept for compatibility with old applications
    CITY_1 = "ville de résidence"
    CITY_2 = "commune de résidence"
    ID_PIECE_NUMBER_1 = "numéro de la pièce"
    ID_PIECE_NUMBER_2 = "numéro de ta pièce"
    POSTAL_CODE = "code postal"
    TELEPHONE = "numéro de téléphone"


class ApplicationPageInfo(pydantic.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/dossierspageinfo.doc.html"""

    end_cursor: str | None = pydantic.Field(None, alias="endCursor")
    has_next_page: bool = pydantic.Field(alias="hasNextPage")


class DMSMessage(pydantic.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/message.doc.html"""

    created_at: DmsDatetime = pydantic.Field(alias="createdAt")
    email: str

    model_config = pydantic.ConfigDict(validate_by_name=True)


class DMSLabel(pydantic.BaseModel):
    id: str
    name: str


class DemarcheDescriptor(pydantic.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/demarchedescriptor.doc.html"""

    number: int


class DmsApplicationResponse(pydantic.BaseModel):
    """Response from DMS API.
    https://demarches-simplifiees-graphql.netlify.app/dossier.doc.html
    """

    applicant: Applicant = pydantic.Field(alias="demandeur")
    annotations: list[DmsField]
    processed_datetime: DmsDatetime | None = pydantic.Field(None, alias="dateTraitement")
    draft_date: DmsDatetime = pydantic.Field(alias="datePassageEnConstruction")
    fields: list[DmsField] = pydantic.Field(alias="champs")
    filing_date: DmsDatetime = pydantic.Field(alias="dateDepot")
    id: str
    labels: list[DMSLabel]
    latest_modification_datetime: DmsDatetime = pydantic.Field(alias="dateDerniereModification")
    latest_user_fields_modification_datetime: DmsDatetime = pydantic.Field(alias="dateDerniereModificationChamps")
    messages: list[DMSMessage]
    number: int
    on_going_date: DmsDatetime | None = pydantic.Field(None, alias="datePassageEnInstruction")
    procedure: DemarcheDescriptor = pydantic.Field(alias="demarche")
    profile: Profile = pydantic.Field(alias="usager")
    state: GraphQLApplicationStates


class DmsPaginatedResponse(pydantic.BaseModel):
    page_info: ApplicationPageInfo = pydantic.Field(alias="pageInfo")


class DmsProcessApplicationsResponse(DmsPaginatedResponse):
    """Response from DMS API.
    https://demarches-simplifiees-graphql.netlify.app/demarche.doc.html
    """

    dms_applications: list[DmsApplicationResponse] = pydantic.Field(alias="nodes")


class DmsDeletedApplication(pydantic.BaseModel):
    """Response from DMS API.
    https://demarches-simplifiees-graphql.netlify.app/deleteddossier.doc.html
    """

    deletion_datetime: DmsDatetime = pydantic.Field(alias="dateSupression")
    id: str
    number: int
    reason: str
    state: GraphQLApplicationStates


class DmsDeletedApplicationsResponse(DmsPaginatedResponse):
    dms_deleted_applications: list[DmsDeletedApplication] = pydantic.Field(alias="nodes")
