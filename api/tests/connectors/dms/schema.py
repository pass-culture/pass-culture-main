import graphql as gql

from . import fixtures


ISO8601DateTime = gql.GraphQLScalarType(
    name="ISO8601DateTime", description="ISO8601 DateTime", serialize=lambda d: d.isoformat()
)

address_type_enum = gql.GraphQLEnumType(
    "AddressType",
    {
        "housenumber": gql.GraphQLEnumValue("housenumber", description="numéro « à la plaque »"),
        "street": gql.GraphQLEnumValue(
            "street", description="position « à la voie », placé approximativement au centre de celle-ci"
        ),
        "municipality": gql.GraphQLEnumValue("municipality", description="numéro « à la commune »"),
        "locality": gql.GraphQLEnumValue("locality", description="lieu-dit"),
    },
    description="Type d'adresse",
)

typed_de_champ_enum = gql.GraphQLEnumType(
    "TypeDeChamp",
    {
        "text": gql.GraphQLEnumValue(
            "text",
            description="Texte",
        ),
        "textarea": gql.GraphQLEnumValue(
            "textarea",
            description="Zone de texte",
        ),
        "date": gql.GraphQLEnumValue(
            "date",
            description="Date",
        ),
        "datetime": gql.GraphQLEnumValue(
            "datetime",
            description="Date et Heure",
        ),
        "number": gql.GraphQLEnumValue(
            "number",
            description="Nombre",
        ),
        "decimal_number": gql.GraphQLEnumValue(
            "decimal_number",
            description="Nombre décimal",
        ),
        "integer_number": gql.GraphQLEnumValue(
            "integer_number",
            description="Nombre entier",
        ),
        "checkbox": gql.GraphQLEnumValue(
            "checkbox",
            description="Case à cocher",
        ),
        "civilite": gql.GraphQLEnumValue(
            "civilite",
            description="Civilité",
        ),
        "email": gql.GraphQLEnumValue(
            "email",
            description="Email",
        ),
        "phone": gql.GraphQLEnumValue(
            "phone",
            description="Téléphone",
        ),
        "address": gql.GraphQLEnumValue(
            "address",
            description="Adresse",
        ),
        "yes_no": gql.GraphQLEnumValue(
            "yes_no",
            description="Oui/Non",
        ),
        "drop_down_list": gql.GraphQLEnumValue(
            "drop_down_list",
            description="Choix parmi une liste",
        ),
        "multiple_drop_down_list": gql.GraphQLEnumValue(
            "multiple_drop_down_list",
            description="Choix multiples",
        ),
        "linked_drop_down_list": gql.GraphQLEnumValue(
            "linked_drop_down_list",
            description="Deux menus déroulants liés",
        ),
        "pays": gql.GraphQLEnumValue(
            "pays",
            description="Pays",
        ),
        "regions": gql.GraphQLEnumValue(
            "regions",
            description="Régions",
        ),
        "departements": gql.GraphQLEnumValue(
            "departements",
            description="Départements",
        ),
        "communes": gql.GraphQLEnumValue(
            "communes",
            description="Communes",
        ),
        "engagement": gql.GraphQLEnumValue(
            "engagement",
            description="Engagement",
        ),
        "header_section": gql.GraphQLEnumValue(
            "header_section",
            description="Titre de section",
        ),
        "explication": gql.GraphQLEnumValue(
            "explication",
            description="Explication",
        ),
        "dossier_link": gql.GraphQLEnumValue(
            "dossier_link",
            description="Lien vers un autre dossier",
        ),
        "piece_justificative": gql.GraphQLEnumValue(
            "piece_justificative",
            description="Pièce justificative",
        ),
        "siret": gql.GraphQLEnumValue(
            "siret",
            description="SIRET",
        ),
        "carte": gql.GraphQLEnumValue(
            "carte",
            description="Carte",
        ),
        "repetition": gql.GraphQLEnumValue(
            "repetition",
            description="Bloc répétable",
        ),
        "titre_identite": gql.GraphQLEnumValue(
            "titre_identite",
            description="Titre identité",
        ),
        "iban": gql.GraphQLEnumValue(
            "iban",
            description="Iban",
        ),
        "annuaire_education": gql.GraphQLEnumValue(
            "annuaire_education",
            description="Annuaire de l’éducation",
        ),
        "cnaf": gql.GraphQLEnumValue(
            "cnaf",
            description="Données de la Caisse nationale des allocations familiales",
        ),
        "dgfip": gql.GraphQLEnumValue(
            "dgfip",
            description="Données de la Direction générale des Finances publiques",
        ),
        "pole_emploi": gql.GraphQLEnumValue(
            "pole_emploi",
            description="Situation Pôle emploi",
        ),
        "mesri": gql.GraphQLEnumValue(
            "mesri",
            description="Données du Ministère de l’Enseignement Supérieur, de la Recherche et de l’Innovation",
        ),
    },
    description="Type de champ",
)

dossier_state_enum = gql.GraphQLEnumType(
    "DossierState",
    {
        "en_construction": gql.GraphQLEnumValue(
            "en_construction",
            description="En construction",
        ),
        "en_instruction": gql.GraphQLEnumValue(
            "en_instruction",
            description="En instruction",
        ),
        "accepte": gql.GraphQLEnumValue(
            "accepte",
            description="Accepté",
        ),
        "refuse": gql.GraphQLEnumValue(
            "refuse",
            description="Refusé",
        ),
        "sans_suite": gql.GraphQLEnumValue(
            "sans_suite",
            description="Classé sans suite",
        ),
    },
    description="Etat du dossier",
)

order_enum = gql.GraphQLEnumType(
    "Order",
    {
        "ASC": gql.GraphQLEnumValue(
            "ASC",
            description="L’ordre ascendant",
        ),
        "DESC": gql.GraphQLEnumValue(
            "DESC",
            description="L’ordre descendant",
        ),
    },
    description="Ordre",
)

dossier_declarative_state_enum = gql.GraphQLEnumType(
    "DossierDeclarativeState",
    {
        "en_instruction": gql.GraphQLEnumValue(
            "en_instruction",
            description="En instruction",
        ),
        "accepte": gql.GraphQLEnumValue(
            "accepte",
            description="Accepté",
        ),
    },
)

demarche_state_enum = gql.GraphQLEnumType(
    "DemarcheState",
    {
        "brouillon": gql.GraphQLEnumValue(
            "brouillon",
            description="Brouillon",
        ),
        "publiee": gql.GraphQLEnumValue(
            "publiee",
            description="Publiée",
        ),
        "close": gql.GraphQLEnumValue(
            "close",
            description="Close",
        ),
        "depubliee": gql.GraphQLEnumValue(
            "depubliee",
            description="Depubliée",
        ),
    },
    description="Etat de la démarche",
)

civilite_enum = gql.GraphQLEnumType(
    "Civilite",
    {
        "M": gql.GraphQLEnumValue(
            "M",
            description="Monsieur",
        ),
        "Mme": gql.GraphQLEnumValue(
            "Mme",
            description="Madame",
        ),
    },
)

champ_descriptor_type = gql.GraphQLObjectType(
    name="ChampDescriptor",
    fields={
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLInt)),
        "description": gql.GraphQLField(gql.GraphQLString),
        "label": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "options": gql.GraphQLField(gql.GraphQLList(gql.GraphQLNonNull(gql.GraphQLString))),
        "required": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLBoolean)),
        "type": gql.GraphQLNonNull(typed_de_champ_enum),
    },
)


page_info_type = gql.GraphQLObjectType(
    name="PageInfo",
    fields={
        "endCursor": gql.GraphQLField(gql.GraphQLString),
        "hasNextPage": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLBoolean)),
        "hasPreviousPage": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLBoolean)),
        "startCursor": gql.GraphQLField(gql.GraphQLString),
    },
)

deleted_dossier_type = gql.GraphQLObjectType(
    name="DeletedDossier",
    fields={
        "dateSuppression": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
        "number": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLInt)),
        "reason": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "state": gql.GraphQLField(gql.GraphQLNonNull(dossier_state_enum)),
    },
)

deleted_dossier_edge_type = gql.GraphQLObjectType(
    name="DeletedDossierEdge",
    fields={
        "cursor": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "node": deleted_dossier_type,
    },
)

deleted_dossier_connection_type = gql.GraphQLObjectType(
    name="DeletedDossierConnection",
    fields={
        "edges": gql.GraphQLField(gql.GraphQLList(deleted_dossier_edge_type)),
        "nodes": gql.GraphQLField(gql.GraphQLList(deleted_dossier_type)),
        "pageInfo": gql.GraphQLField(gql.GraphQLNonNull(page_info_type)),
    },
)


champ_type = gql.GraphQLInterfaceType(
    name="Champ",
    fields={
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
        "label": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "stringValue": gql.GraphQLField(gql.GraphQLString),
    },
    resolve_type=lambda champ, _info, _type: {
        "RepetitionChamp": repetition_champ_type.name,
        "DossierLinkChamp": dossier_link_champ.name,
        "LinkedDropDownListChamp": linked_drop_down_list_champ_type.name,
        "MultipleDropDownListChamp": multiple_drop_down_list_champ_type.name,
        "AddressChamp": address_champ_type.name,
        "PieceJustificativeChamp": piece_justificative_champ_type.name,
    }[champ.__class__.__name__],
)


repetition_champ_type = gql.GraphQLObjectType(
    name="RepetitionChamp",
    interfaces=[champ_type],
    fields={
        "champs": gql.GraphQLField(gql.GraphQLList(gql.GraphQLNonNull(champ_type))),
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
        "label": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "stringValue": gql.GraphQLField(gql.GraphQLString),
    },
)


profile_type = gql.GraphQLObjectType(
    name="Profile",
    fields={
        "email": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
    },
)

avis_type = gql.GraphQLObjectType(
    name="Avis",
    fields={
        "attachment": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "claimant": gql.GraphQLField(gql.GraphQLNonNull(profile_type)),
        "dateQuestion": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "dateReponse": gql.GraphQLField(gql.GraphQLString),
        "expert": gql.GraphQLField(gql.GraphQLNonNull(profile_type)),
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
        "instructeur": gql.GraphQLField(gql.GraphQLNonNull(profile_type)),
        "question": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "reponse": gql.GraphQLField(gql.GraphQLString),
    },
)

demandeur_interface = gql.GraphQLInterfaceType(
    name="Demandeur",
    fields={
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
    },
    resolve_type=lambda demandeur, _info, _type: {
        "PersonnePhysique": personne_physique_type.name,
    }[demandeur.__class__.__name__],
)


personne_physique_type = gql.GraphQLObjectType(
    name="PersonnePhysique",
    interfaces=[demandeur_interface],
    fields={
        "civilite": gql.GraphQLField(gql.GraphQLNonNull(civilite_enum)),
        "dateDeNaissance": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
        "nom": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "prenom": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
    },
)


demarche_descriptor_type = gql.GraphQLObjectType(
    name="DemarcheDescriptor",
    fields={
        "date_creation": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "date_depublication": gql.GraphQLField(gql.GraphQLString),
        "date_derniere_modification": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "date_fermeture": gql.GraphQLField(gql.GraphQLString),
        "date_publication": gql.GraphQLField(gql.GraphQLString),
        "declarative": gql.GraphQLField(dossier_declarative_state_enum),
        "description": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
        "number": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLInt)),
        "state": gql.GraphQLField(gql.GraphQLNonNull(demarche_state_enum)),
        "title": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
    },
)


groupe_instructeur_type = gql.GraphQLObjectType(
    name="GroupeInstructeur",
    fields={
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
        "instructeurs": gql.GraphQLField(gql.GraphQLList(gql.GraphQLNonNull(profile_type))),
        "label": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "number": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLInt)),
    },
)


message_type = gql.GraphQLObjectType(
    name="Message",
    fields={
        "attachment": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "body": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "createdAt": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "email": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
    },
)


revision_type = gql.GraphQLObjectType(
    name="Revision",
    fields={
        "annotation_descriptors": gql.GraphQLField(gql.GraphQLList(gql.GraphQLNonNull(champ_descriptor_type))),
        "champ_descriptors": gql.GraphQLField(gql.GraphQLList(gql.GraphQLNonNull(champ_descriptor_type))),
        "date_creation": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "date_publication": gql.GraphQLField(gql.GraphQLString),
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
    },
)


traitement_type = gql.GraphQLObjectType(
    name="Traitement",
    fields={
        "date_traitement": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "email_agent_traitant": gql.GraphQLField(gql.GraphQLString),
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
        "motivation": gql.GraphQLField(gql.GraphQLString),
        "state": gql.GraphQLField(gql.GraphQLNonNull(dossier_state_enum)),
    },
)


file_type = gql.GraphQLObjectType(
    name="File",
    fields={
        "byteSizeBigInt": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLInt)),
        "checksum": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "contentType": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "filename": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "url": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
    },
)
dossier_type = gql.GraphQLObjectType(
    name="Dossier",
    fields={
        "annotations": gql.GraphQLField(gql.GraphQLList(gql.GraphQLNonNull(champ_type))),
        "archived": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLBoolean)),
        "attestation": gql.GraphQLField(file_type),
        "avis": gql.GraphQLField(gql.GraphQLList(gql.GraphQLNonNull(avis_type))),
        "champs": gql.GraphQLField(gql.GraphQLList(gql.GraphQLNonNull(champ_type))),
        "dateDepot": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "dateDerniereModification": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "dateExpiration": gql.GraphQLField(gql.GraphQLString),
        "datePassageEnConstruction": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "datePassageEnInstruction": gql.GraphQLField(gql.GraphQLString),
        "dateSuppressionParAdministration": gql.GraphQLField(gql.GraphQLString),
        "dateSuppressionParUsager": gql.GraphQLField(gql.GraphQLString),
        "dateTraitement": gql.GraphQLField(gql.GraphQLString),
        "demandeur": gql.GraphQLField(gql.GraphQLNonNull(demandeur_interface)),
        "demarche": gql.GraphQLField(gql.GraphQLNonNull(demarche_descriptor_type)),
        "geojson": gql.GraphQLField(gql.GraphQLString),
        "groupeInstructeur": gql.GraphQLField(gql.GraphQLNonNull(groupe_instructeur_type)),
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
        "instructeurs": gql.GraphQLField(gql.GraphQLList(gql.GraphQLNonNull(profile_type))),
        "messages": gql.GraphQLField(gql.GraphQLList(gql.GraphQLNonNull(message_type))),
        "motivation": gql.GraphQLField(gql.GraphQLString),
        "motivationAttachment": gql.GraphQLField(file_type),
        "number": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLInt)),
        "pdf": gql.GraphQLField(file_type),
        "revision": gql.GraphQLField(gql.GraphQLNonNull(revision_type)),
        "state": gql.GraphQLField(gql.GraphQLNonNull(dossier_state_enum)),
        "traitements": gql.GraphQLField(gql.GraphQLList(gql.GraphQLNonNull(traitement_type))),
        "usager": gql.GraphQLField(gql.GraphQLNonNull(profile_type)),
    },
)

dossier_edge_type = gql.GraphQLObjectType(
    name="DossierEdge",
    fields={
        "cursor": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "node": gql.GraphQLField(gql.GraphQLNonNull(dossier_type)),
    },
)

dossier_connection_type = gql.GraphQLObjectType(
    name="DossierConnection",
    fields={
        "edges": gql.GraphQLField(gql.GraphQLList(dossier_edge_type)),
        "nodes": gql.GraphQLField(
            gql.GraphQLList(dossier_type),
            resolve=lambda _source, _info, applicationNumber=1, **kwargs: [fixtures.dossier_1],
        ),
        "pageInfo": gql.GraphQLField(gql.GraphQLNonNull(page_info_type)),
    },
)


geojson_type = gql.GraphQLObjectType(
    name="GeoJSON",
    fields={
        "coordinates": gql.GraphQLField(
            gql.GraphQLNonNull(
                gql.GraphQLList(gql.GraphQLNonNull(gql.GraphQLList(gql.GraphQLScalarType("Coordinates"))))
            )
        ),
        "type": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
    },
)

address_type = gql.GraphQLObjectType(
    name="Address",
    fields={
        "cityCode": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "cityName": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "departmentCode": gql.GraphQLField(gql.GraphQLString),
        "departmentName": gql.GraphQLField(gql.GraphQLString),
        "geometry": gql.GraphQLField(geojson_type),
        "label": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "postalCode": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "regionCode": gql.GraphQLField(gql.GraphQLString),
        "regionName": gql.GraphQLField(gql.GraphQLString),
        "streetAddress": gql.GraphQLField(gql.GraphQLString),
        "streetName": gql.GraphQLField(gql.GraphQLString),
        "streetNumber": gql.GraphQLField(gql.GraphQLString),
        "type": gql.GraphQLField(gql.GraphQLNonNull(address_type_enum)),
    },
)


dossier_link_champ = gql.GraphQLObjectType(
    name="DossierLinkChamp",
    interfaces=[champ_type],
    fields={
        "dossier": gql.GraphQLField(gql.GraphQLNonNull(dossier_type)),
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
        "label": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "stringValue": gql.GraphQLField(gql.GraphQLString),
    },
)


linked_drop_down_list_champ_type = gql.GraphQLObjectType(
    name="LinkedDropDownListChamp",
    interfaces=[champ_type],
    fields={
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
        "label": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "primaryValue": gql.GraphQLField(gql.GraphQLString),
        "secondaryValue": gql.GraphQLField(gql.GraphQLString),
        "stringValue": gql.GraphQLField(gql.GraphQLString),
    },
)


multiple_drop_down_list_champ_type = gql.GraphQLObjectType(
    name="MultipleDropDownListChamp",
    interfaces=[champ_type],
    fields={
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
        "label": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "stringValue": gql.GraphQLField(gql.GraphQLString),
        "values": gql.GraphQLField(gql.GraphQLList(gql.GraphQLNonNull(gql.GraphQLString))),
    },
)


piece_justificative_champ_type = gql.GraphQLObjectType(
    name="PieceJustificativeChamp",
    interfaces=[champ_type],
    fields={
        "file": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
        "label": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "stringValue": gql.GraphQLField(gql.GraphQLString),
    },
)

address_champ_type = gql.GraphQLObjectType(
    name="AddressChamp",
    interfaces=[champ_type],
    fields={
        "address": gql.GraphQLField(gql.GraphQLNonNull(address_type)),
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
        "label": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "stringValue": gql.GraphQLField(gql.GraphQLString),
    },
)


service_type = gql.GraphQLObjectType(
    name="Service",
    fields={
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
        # other fields not used by us yet:
        #   nom: String!
        #   organisme: String!
        #   typeOrganisme: TypeOrganisme!
    },
)

demarche_type = gql.GraphQLObjectType(
    "Demarche",
    fields={
        "annotationDescriptors": gql.GraphQLField(gql.GraphQLList(gql.GraphQLNonNull(champ_descriptor_type))),
        "champDescriptors": gql.GraphQLField(gql.GraphQLList(gql.GraphQLNonNull(champ_descriptor_type))),
        "dateCreation": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "dateDepublication": gql.GraphQLField(gql.GraphQLString),
        "dateDerniereModification": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
        "dateFermeture": gql.GraphQLField(gql.GraphQLString),
        "datePublication": gql.GraphQLField(gql.GraphQLString),
        "declarative": gql.GraphQLField(
            dossier_declarative_state_enum,
            description="Pour une démarche déclarative, état cible des dossiers à valider automatiquement",
        ),
        "deletedDossiers": gql.GraphQLField(
            gql.GraphQLNonNull(deleted_dossier_connection_type),
            args={
                "after": gql.GraphQLArgument(gql.GraphQLString),
                "before": gql.GraphQLArgument(gql.GraphQLString),
                "first": gql.GraphQLArgument(gql.GraphQLInt),
                "last": gql.GraphQLArgument(gql.GraphQLInt),
                "order": gql.GraphQLArgument(order_enum, default_value="ASC"),
                "deletedSince": gql.GraphQLArgument(gql.GraphQLString),
            },
        ),
        "description": gql.GraphQLField(
            gql.GraphQLNonNull(gql.GraphQLString), description="Description de la démarche"
        ),
        "dossiers": gql.GraphQLField(
            gql.GraphQLNonNull(dossier_connection_type),
            args={
                "after": gql.GraphQLArgument(gql.GraphQLString),
                "before": gql.GraphQLArgument(gql.GraphQLString),
                "first": gql.GraphQLArgument(gql.GraphQLInt),
                "last": gql.GraphQLArgument(gql.GraphQLInt),
                "order": gql.GraphQLArgument(order_enum),
                "createdSince": gql.GraphQLArgument(ISO8601DateTime),
                "updatedSince": gql.GraphQLArgument(ISO8601DateTime),
                "state": gql.GraphQLArgument(dossier_state_enum),
                "archived": gql.GraphQLArgument(gql.GraphQLBoolean),
                "revision": gql.GraphQLArgument(gql.GraphQLID),
                "maxRevision": gql.GraphQLArgument(gql.GraphQLID),
                "minRevision": gql.GraphQLArgument(gql.GraphQLID),
            },
        ),
        "draftRevision": gql.GraphQLField(gql.GraphQLNonNull(revision_type)),
        "groupeInstructeurs": gql.GraphQLList(gql.GraphQLNonNull(groupe_instructeur_type)),
        "id": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLID)),
        "number": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLInt)),
        "publishedRevision": gql.GraphQLField(revision_type),
        "revisions": gql.GraphQLList(gql.GraphQLNonNull(revision_type)),
        "service": gql.GraphQLField(gql.GraphQLNonNull(service_type)),
        "state": gql.GraphQLField(gql.GraphQLNonNull(demarche_state_enum)),
        "title": gql.GraphQLField(gql.GraphQLNonNull(gql.GraphQLString)),
    },
)


query_type = gql.GraphQLObjectType(
    "Query",
    fields={
        "demarche": gql.GraphQLField(
            gql.GraphQLNonNull(demarche_type),
            args={
                "number": gql.GraphQLArgument(gql.GraphQLNonNull(gql.GraphQLInt)),
            },
            resolve=lambda _source, _info, number=8888: fixtures.demarche_1,
        ),
        "dossier": gql.GraphQLField(
            gql.GraphQLNonNull(dossier_type),
            args={
                "number": gql.GraphQLArgument(gql.GraphQLNonNull(gql.GraphQLInt)),
            },
            resolve=lambda _source, _info, number=1: fixtures.dossier_1,
        ),
        "groupeInstructeur": gql.GraphQLField(
            gql.GraphQLNonNull(groupe_instructeur_type),
            args={
                "number": gql.GraphQLArgument(gql.GraphQLNonNull(gql.GraphQLInt)),
            },
        ),
    },
)


DmsSchema = gql.GraphQLSchema(
    query=query_type,
    types=[
        # root types
        demarche_type,
        dossier_type,
        # types implementing interfaces
        personne_physique_type,
        repetition_champ_type,
        dossier_link_champ,
        linked_drop_down_list_champ_type,
        multiple_drop_down_list_champ_type,
        piece_justificative_champ_type,
        address_champ_type,
    ],
)
