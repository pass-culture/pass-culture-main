import pydantic.v1 as pydantic_v1


dossier_default_passage_en_construction = "2020-03-24T12:35:51+01:00"
dossier_default_date_depot = "2020-03-25T12:35:51+01:00"
demarche_default_date_creation = "2020-03-25T12:35:51+01:00"


class Address(pydantic_v1.BaseModel):
    cityCode: str = "75001"
    cityName: str = "Paris"
    departmentCode: str | None = None
    departmentName: str | None = None
    geometry: str | None = None
    label: str = "1 rue de la République, 75001 Paris"
    postalCode: str = "75001"
    regionCode: str | None = None
    regionName: str | None = None
    streetAddress: str | None = None
    streetName: str | None = None
    streetNumber: str | None = None
    type: str = "housenumber"


class File(pydantic_v1.BaseModel):
    filename: str = "file.pdf"
    url: str = "https://example.com/file.pdf"


class Champ(pydantic_v1.BaseModel):
    id: int
    label: str
    stringValue: str | None


class AddressChamp(Champ):
    address: Address


class RepetitionChamp(Champ):
    champs: list[Champ]


class DossierLinkChamp(Champ):
    dossier: "Dossier"


class LinkedDropDownListChamp(Champ):
    primaryValue: str | None
    secondaryValue: str | None


class MultipleDropDownListChamp(Champ):
    values: list[str]


class PieceJustificativeChamp(Champ):
    file: str


class Demandeur(pydantic_v1.BaseModel):
    id: str = "demandeur_id"


class PersonnePhysique(Demandeur):
    civilite: str
    dateDeNaissance: str
    id: str
    nom: str
    prenom: str


class Revision(pydantic_v1.BaseModel):
    annotation_descriptors: list[Champ] = []
    champ_descriptors: list[Champ] = []
    date_creation: str = demarche_default_date_creation
    date_publication: str = demarche_default_date_creation
    id: str = "revision_id"


class Service(pydantic_v1.BaseModel):
    id: str


class PageInfo(pydantic_v1.BaseModel):
    endCursor: str | None
    hasNextPage: bool = False
    hasPreviousPage: bool = False
    startCursor: str | None


class DossierConnection(pydantic_v1.BaseModel):
    pageInfo: PageInfo = PageInfo()
    edges: list[dict] = []
    nodes: list[dict] = []


class Demarche(pydantic_v1.BaseModel):
    annotationDescriptors: list = []
    champDescriptors: list = []
    dateCreation: str = demarche_default_date_creation
    dateDepublication: str | None = None
    dateDerniereModification: str = demarche_default_date_creation
    dateFermeture: str | None = None
    datePublication: str | None = None
    declarative: str | None = None
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


class GroupeInstructeur(pydantic_v1.BaseModel):
    id: str
    number: int
    label: str


class Profile(pydantic_v1.BaseModel):
    id: str = "profile_id"
    email: str = "default_email@example.com"


class Message(pydantic_v1.BaseModel):
    createdAt: str = dossier_default_date_depot
    email: str = "message_email@example.com"


class Label(pydantic_v1.BaseModel):
    id: str = "label_id"
    name: str = "Label Name"


class Dossier(pydantic_v1.BaseModel):
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
    dateDerniereModificationChamps: str = dossier_default_date_depot
    dateExpiration: str | None = None
    datePassageEnConstruction: str = dossier_default_passage_en_construction
    datePassageEnInstruction: str | None = None
    dateSuppressionParAdministration: str | None = None
    dateSuppressionParUsager: str | None = None
    dateTraitement: str | None = None
    demandeur: Demandeur = PersonnePhysique(
        id="personne_id", civilite="M", dateDeNaissance="2020-03-25", nom="Stiles", prenom="John"
    )
    demarche: Demarche = Demarche(id="demarche_id", number=1, title="titre de la démarche")
    geojson: str | None = None
    groupeInstructeur: GroupeInstructeur = GroupeInstructeur(id="groupe_instructeur_id", number=1, label="défaut")
    id: str = "RandomGeneratedId"
    instructeurs: list[Profile] = [Profile()]
    labels: list[Label] = [Label()]
    messages: list[Message] = [Message()]
    motivation: str | None = None
    motivationAttachment: File | None = None
    number: int = 1
    pdf: str | None = None
    revision: Revision = Revision()
    state: str = "en_construction"
    traitements: list = []
    usager: Profile = Profile(id="usager_id", email="lucille.ellingson@example.com")


dossier_1 = Dossier(dossier_id="RandomGeneratedId", number=1)


demarche_1 = Demarche(id="RandomGeneratedId", number=1, dossiers=DossierConnection(nodes=[dossier_1]))
