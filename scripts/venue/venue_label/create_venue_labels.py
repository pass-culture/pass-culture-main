from typing import List

from models import VenueLabelSQLEntity
from repository import repository


def create_venue_labels():
    venue_labels = [
        "Architecture contemporaine remarquable",
        "CAC - Centre d'art contemporain d'intérêt national",
        "CCN - Centre chorégraphique national",
        "CDCN - Centre de développement chorégraphique national",
        "CDN - Centre dramatique national",
        "Cinéma d'art et d'essai",
        "CNAREP - Centre national des arts de la rue et de l'espace public",
        "CNCM - Centre national de création musicale",
        "CRC/CRI - Conservatoire à rayonnement communal ou intercommunal",
        "CRD - Conservatoire à rayonnement départemental",
        "CRR - Conservatoire à rayonnement régional",
        "FRAC - Fonds régional d'art contemporain",
        "Jardin remarquable",
        "LIR - Librairie indépendante de référence",
        "Maison des illustres",
        "Monuments historiques",
        "Musée de France",
        "Opéra national en région",
        "Orchestre national en région",
        "Patrimoine européen",
        "PNC - Pôle national du cirque",
        "Scène nationale",
        "Scènes conventionnées",
        "Sites patrimoniaux remarquables",
        "SMAC - Scène de musiques actuelles",
        "Théâtres nationaux",
        "UNESCO - Patrimoine mondial",
        "Ville et Pays d'art et d'histoire"
    ]

    save_new_venue_labels(venue_labels)


def save_new_venue_labels(venue_labels: List[str]):
    venue_label_sql_entities = []
    for venue_label in venue_labels:
        venue_label_sql_entity = VenueLabelSQLEntity()
        venue_label_sql_entity.label = venue_label
        venue_label_sql_entities.append(venue_label_sql_entity)
    repository.save(*venue_label_sql_entities)
