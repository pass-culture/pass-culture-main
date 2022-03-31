import datetime
import enum
import typing

import pydantic


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
    2 procédures sont acceptées:
    - Jeune de nationalité étrangère: DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID_v4_ET
    - Jeune de nationalité française: DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID_v4_FR
    """

    ACTIVITY_ET = "Merci d' indiquer ton statut"
    ACTIVITY_FR = "Merci d'indiquer ton statut"
    ADDRESS_ET = "Quelle est ton adresse de résidence ?"
    ADDRESS_FR = "Quelle est ton adresse de résidence"
    BIRTH_DATE_ET = "Quelle est ta date de naissance ?"
    BIRTH_DATE_FR = "Quelle est votre date de naissance"
    DEPARTMENT_ET = "Veuillez indiquer votre département"
    DEPARTMENT_FR = "Veuillez indiquer votre département"
    ID_PIECE_NUMBER_ET = "Quel est le numéro de la pièce que tu viens de saisir ?"
    ID_PIECE_NUMBER_FR = "Quel est le numéro de la pièce que tu viens de saisir ?"
    POSTAL_CODE_ET = "Quel est le code postal de ta commune de résidence ?"
    POSTAL_CODE_FR = "Quel est le code postal de ta commune de résidence ? (ex : 25370)"
    TELEPHONE_ET = "Quel est ton numéro de téléphone ?"
    TELEPHONE_FR = "Quel est ton numéro de téléphone ?"


class ApplicationPageInfo(pydantic.BaseModel):
    """https://demarches-simplifiees-graphql.netlify.app/dossierspageinfo.doc.html"""

    end_cursor: typing.Optional[str] = pydantic.Field(None, alias="endCursor")
    has_next_page: bool = pydantic.Field(alias="hasNextPage")


class DmsApplicationResponse(pydantic.BaseModel):
    """Response from DMS API.
    https://demarches-simplifiees-graphql.netlify.app/dossier.doc.html
    """

    applicant: Applicant = pydantic.Field(alias="demandeur")
    done_date: typing.Optional[datetime.datetime] = pydantic.Field(None, alias="dateTraitement")
    draft_date: datetime.datetime = pydantic.Field(alias="datePassageEnConstruction")
    fields: list[DmsField] = pydantic.Field(alias="champs")
    filing_date: datetime.datetime = pydantic.Field(alias="dateDepot")
    id: str
    latest_modification_date: datetime.datetime = pydantic.Field(alias="dateDerniereModification")
    number: int
    on_going_date: typing.Optional[datetime.datetime] = pydantic.Field(None, alias="datePassageEnInstruction")
    profile: Profile = pydantic.Field(alias="usager")
    state: GraphQLApplicationStates


class DmsProcessApplicationsResponse(pydantic.BaseModel):
    """Response from DMS API.
    https://demarches-simplifiees-graphql.netlify.app/demarche.doc.html
    """

    dms_applications: list[DmsApplicationResponse] = pydantic.Field(alias="nodes")
    page_info: ApplicationPageInfo = pydantic.Field(alias="pageInfo")
