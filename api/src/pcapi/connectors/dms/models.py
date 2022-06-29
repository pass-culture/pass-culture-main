import datetime
import enum
import typing

import pydantic
import pytz


def parse_dms_datetime(value: typing.Optional[datetime.datetime]) -> typing.Optional[datetime.datetime]:
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

    birth_date: typing.Optional[datetime.date] = pydantic.Field(None, alias="dateDeNaissance")
    civility: Civility = pydantic.Field(alias="civilite")
    first_name: str = pydantic.Field(alias="prenom")
    id: str
    last_name: str = pydantic.Field(alias="nom")


class DmsField(pydantic.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/champ.doc.html"""

    id: str
    label: str
    value: typing.Optional[str] = pydantic.Field(None, alias="stringValue")


class FieldLabel(enum.Enum):
    """
    Ces champs sont tirés des labels des questions des démarches DMS
    """

    ACTIVITY_ET = "Merci d' indiquer ton statut"
    ACTIVITY_FR = "Merci d'indiquer ton statut"
    ADDRESS_ET = "Quelle est ton adresse de résidence ?"
    ADDRESS_FR = "Quelle est ton adresse de résidence"
    BIRTH_DATE_ET = "Quelle est ta date de naissance ?"
    BIRTH_DATE_FR = "Quelle est votre date de naissance"
    CITY_FR = "Quelle est ta ville de résidence ?"
    CITY_ET = "Quelle est ta ville de résidence ?"
    ID_PIECE_NUMBER_ET = "Quel est le numéro de la pièce que tu viens de saisir ?"
    ID_PIECE_NUMBER_FR = "Quel est le numéro de la pièce que tu viens de saisir ?"
    ID_PIECE_NUMBER_PROCEDURE_4765 = "Quel est le numéro de la pièce que vous venez de saisir ?"
    POSTAL_CODE_ET = "Quel est le code postal de ta commune de résidence ?"
    POSTAL_CODE_FR = "Quel est le code postal de ta commune de résidence ? (ex : 25370)"
    POSTAL_CODE_OLD = "Quel est le code postal de votre commune de résidence ?"
    TELEPHONE_ET = "Quel est ton numéro de téléphone ?"
    TELEPHONE_FR = "Quel est ton numéro de téléphone ?"


class ApplicationPageInfo(pydantic.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/dossierspageinfo.doc.html"""

    end_cursor: typing.Optional[str] = pydantic.Field(None, alias="endCursor")
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

    id: int = pydantic.Field(alias="number")


class DmsApplicationResponse(pydantic.BaseModel):
    """Response from DMS API.
    https://demarches-simplifiees-graphql.netlify.app/dossier.doc.html
    """

    applicant: Applicant = pydantic.Field(alias="demandeur")
    processed_datetime: typing.Optional[datetime.datetime] = pydantic.Field(None, alias="dateTraitement")
    draft_date: datetime.datetime = pydantic.Field(alias="datePassageEnConstruction")
    fields: list[DmsField] = pydantic.Field(alias="champs")
    filing_date: datetime.datetime = pydantic.Field(alias="dateDepot")
    id: str
    latest_modification_date: datetime.datetime = pydantic.Field(alias="dateDerniereModification")
    messages: list[DMSMessage]
    number: int
    on_going_date: typing.Optional[datetime.datetime] = pydantic.Field(None, alias="datePassageEnInstruction")
    procedure: DemarcheDescriptor = pydantic.Field(alias="demarche")
    profile: Profile = pydantic.Field(alias="usager")
    state: GraphQLApplicationStates

    _format_processed_datetime = pydantic.validator("processed_datetime", allow_reuse=True)(parse_dms_datetime)
    _format_filing_date = pydantic.validator("filing_date", allow_reuse=True)(parse_dms_datetime)
    _format_latest_modification_date = pydantic.validator("latest_modification_date", allow_reuse=True)(
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
