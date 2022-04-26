from pcapi.core.offerers.models import VenueLabel
from pcapi.repository import repository


def create_venue_labels():  # type: ignore [no-untyped-def]
    venue_label_strings = [
        "Architecture contemporaine remarquable",
        "CAC - Centre d'art contemporain d'intérêt national",
        "CCN - Centre chorégraphique national",
        "CDCN - Centre de développement chorégraphique national",
        "CDN - Centre dramatique national",
        "Centre Culturel de Rencontre",
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
        "Théâtre lyrique conventionné d'intérêt national",
        "Théâtres nationaux",
        "UNESCO - Patrimoine mondial",
        "Ville et Pays d'art et d'histoire",
    ]

    save_new_venue_labels(venue_label_strings)


def save_new_venue_labels(venue_label_strings: list[str]):  # type: ignore [no-untyped-def]
    venue_label_list = []
    for label_string in venue_label_strings:
        venue_label = VenueLabel()
        venue_label.label = label_string
        venue_label_list.append(venue_label)
    repository.save(*venue_label_list)
