import datetime
import enum

import pydantic
import pytz


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


class DmsField(pydantic.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/champ.doc.html"""

    id: str
    label: str
    value: str | None = pydantic.Field(None, alias="stringValue")


class FieldLabelKeyword(enum.Enum):
    """
    Ces champs sont tirés des labels des questions des démarches DMS
    """

    ACTIVITY = "statut"
    ADDRESS = "adresse de résidence"
    BIRTH_DATE = "date de naissance"
    CITY_1 = "ville de résidence"
    CITY_2 = "commune de résidence"
    ID_PIECE_NUMBER = "numéro de la pièce"
    POSTAL_CODE = "code postal"
    TELEPHONE = "numéro de téléphone"


class ApplicationPageInfo(pydantic.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/dossierspageinfo.doc.html"""

    end_cursor: str | None = pydantic.Field(None, alias="endCursor")
    has_next_page: bool = pydantic.Field(alias="hasNextPage")


class DMSMessage(pydantic.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/message.doc.html"""

    created_at: datetime.datetime = pydantic.Field(alias="createdAt")
    email: str

    class Config:
        allow_population_by_field_name = True

    _format_created_at = pydantic.validator("created_at", allow_reuse=True)(parse_dms_datetime)


class DemarcheDescriptor(pydantic.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/demarchedescriptor.doc.html"""

    number: int


class DmsApplicationResponse(pydantic.BaseModel):
    """Response from DMS API.
    https://demarches-simplifiees-graphql.netlify.app/dossier.doc.html
    """

    applicant: Applicant = pydantic.Field(alias="demandeur")
    processed_datetime: datetime.datetime | None = pydantic.Field(None, alias="dateTraitement")
    draft_date: datetime.datetime = pydantic.Field(alias="datePassageEnConstruction")
    fields: list[DmsField] = pydantic.Field(alias="champs")
    filing_date: datetime.datetime = pydantic.Field(alias="dateDepot")
    id: str
    latest_modification_datetime: datetime.datetime = pydantic.Field(alias="dateDerniereModification")
    messages: list[DMSMessage]
    number: int
    on_going_date: datetime.datetime | None = pydantic.Field(None, alias="datePassageEnInstruction")
    procedure: DemarcheDescriptor = pydantic.Field(alias="demarche")
    profile: Profile = pydantic.Field(alias="usager")
    state: GraphQLApplicationStates

    _format_processed_datetime = pydantic.validator("processed_datetime", allow_reuse=True)(parse_dms_datetime)
    _format_filing_date = pydantic.validator("filing_date", allow_reuse=True)(parse_dms_datetime)
    _format_latest_modification_datetime = pydantic.validator("latest_modification_datetime", allow_reuse=True)(
        parse_dms_datetime
    )
    _format_on_going_date = pydantic.validator("on_going_date", allow_reuse=True)(parse_dms_datetime)


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

    deletion_datetime: datetime.datetime = pydantic.Field(alias="dateSupression")
    id: str
    number: int
    reason: str
    state: GraphQLApplicationStates

    _format_deletion_datetime = pydantic.validator("deletion_datetime", allow_reuse=True)(parse_dms_datetime)


class DmsDeletedApplicationsResponse(DmsPaginatedResponse):
    dms_deleted_applications: list[DmsDeletedApplication] = pydantic.Field(alias="nodes")
