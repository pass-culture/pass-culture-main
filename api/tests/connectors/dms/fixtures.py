from typing import Optional

import pydantic


dossier_default_passage_en_construction = "2020-03-24T12:35:51+01:00"
dossier_default_date_depot = "2020-03-25T12:35:51+01:00"
demarche_default_date_creation = "2020-03-25T12:35:51+01:00"


class Address(pydantic.BaseModel):
    cityCode: str = "75001"
    cityName: str = "Paris"
    departmentCode: Optional[str] = None
    departmentName: Optional[str] = None
    geometry: Optional[str] = None
    label: str = "1 rue de la République, 75001 Paris"
    postalCode: str = "75001"
    regionCode: Optional[str] = None
    regionName: Optional[str] = None
    streetAddress: Optional[str] = None
    streetName: Optional[str] = None
    streetNumber: Optional[str] = None
    type: str = "housenumber"


class File(pydantic.BaseModel):
    filename: str = "file.pdf"
    url: str = "https://example.com/file.pdf"


class Champ(pydantic.BaseModel):
    id: int
    label: str
    stringValue: Optional[str]


class AddressChamp(Champ):
    address: Address


class RepetitionChamp(Champ):
    champs: list[Champ]


class DossierLinkChamp(Champ):
    dossier: "Dossier"


class LinkedDropDownListChamp(Champ):
    primaryValue: Optional[str]
    secondaryValue: Optional[str]


class MultipleDropDownListChamp(Champ):
    values: list[str]


class PieceJustificativeChamp(Champ):
    file: str


class Demandeur(pydantic.BaseModel):
    id: str = "demandeur_id"


class PersonnePhysique(Demandeur):
    civilite: str
    dateDeNaissance: str
    id: str
    nom: str
    prenom: str


class Revision(pydantic.BaseModel):
    annotation_descriptors: list[Champ] = []
    champ_descriptors: list[Champ] = []
    date_creation: str = demarche_default_date_creation
    date_publication: str = demarche_default_date_creation
    id: str = "revision_id"


class Service(pydantic.BaseModel):
    id: str


class PageInfo(pydantic.BaseModel):
    endCursor: Optional[str]
    hasNextPage: bool = False
    hasPreviousPage: bool = False
    startCursor: Optional[str]


class DossierConnection(pydantic.BaseModel):
    pageInfo: PageInfo = PageInfo()
    edges: list[dict] = []
    nodes: list[dict] = []


class Demarche(pydantic.BaseModel):
    annotationDescriptors: list = []
    champDescriptors: list = []
    dateCreation: str = demarche_default_date_creation
    dateDepublication: Optional[str] = None
    dateDerniereModification: str = demarche_default_date_creation
    dateFermeture: Optional[str] = None
    datePublication: Optional[str] = None
    declarative: Optional[str] = None
    deletedDossiers: list = []
    description: str = "description de la démarche"
    dossiers: DossierConnection = DossierConnection()
    draftRevision: Revision = Revision()
    groupeInstructeurs: list = []
    id: str
    number: int
    publishedRevision: Revision = Revision()
    revisions: list[Revision] = []
    service: Service = Service(id="service_id")
    state: str = "en_construction"
    title: str = "titre de la démarche"


class GroupeInstructeur(pydantic.BaseModel):
    id: str
    number: int
    label: str


class Profile(pydantic.BaseModel):
    id: str = "profile_id"
    email: str = "default_email@example.com"


class Message(pydantic.BaseModel):
    createdAt: str = dossier_default_date_depot
    email: str = "message_email@example.com"


class Dossier(pydantic.BaseModel):
    annotations: list = []
    archived: bool = False
    attestation: File = File()
    avis: list = []
    champs: list[Champ] = [
        AddressChamp(id=1, label="champ 1 address", stringValue="valeur 1", address=Address()),
        PieceJustificativeChamp(id=2, label="champ 2 piece justificative", stringValue="valeur 2", file="file_id"),
    ]
    dateDepot: str = dossier_default_date_depot
    dateDerniereModification: str = dossier_default_date_depot
    dateExpiration: Optional[str] = None
    datePassageEnConstruction: str = dossier_default_passage_en_construction
    datePassageEnInstruction: Optional[str] = None
    dateSuppressionParAdministration: Optional[str] = None
    dateSuppressionParUsager: Optional[str] = None
    dateTraitement: Optional[str] = None
    demandeur: Demandeur = PersonnePhysique(
        id="personne_id", civilite="M", dateDeNaissance="2020-03-25", nom="Stiles", prenom="John"
    )
    demarche: Demarche = Demarche(id="demarche_id", number=1, title="titre de la démarche")
    geojson: Optional[str] = None
    groupeInstructeur: GroupeInstructeur = GroupeInstructeur(id="groupe_instructeur_id", number=1, label="défaut")
    id: str = "RandomGeneratedId"
    instructeurs: list[Profile] = [Profile()]
    messages: list[Message] = [Message()]
    motivation: Optional[str] = None
    motivationAttachment: Optional[File] = None
    number: int = 1
    pdf: Optional[str] = None
    revision: Revision = Revision()
    state: str = "en_construction"
    traitements: list = []
    usager: Profile = Profile(id="usager_id", email="lucille.ellingson@example.com")


dossier_1 = Dossier(dossier_id="RandomGeneratedId", number=1)


demarche_1 = Demarche(id="RandomGeneratedId", number=1, dossiers=DossierConnection(nodes=[dossier_1]))
