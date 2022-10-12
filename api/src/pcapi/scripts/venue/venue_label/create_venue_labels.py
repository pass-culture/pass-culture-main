from typing import Tuple

from pcapi.core.offerers.models import VenueLabel
from pcapi.repository import repository


# match ids from staging for synchronization with ADAGE
def create_venue_labels(sandbox: bool = False) -> None:
    venue_label_strings = [
        ("Architecture contemporaine remarquable", 1),
        ("CAC - Centre d'art contemporain d'intérêt national", 2),
        ("CCN - Centre chorégraphique national", 3),
        ("CDCN - Centre de développement chorégraphique national", 4),
        ("CDN - Centre dramatique national", 5),
        ("Cinéma d'art et d'essai", 6),
        ("CNAREP - Centre national des arts de la rue et de l'espace public", 7),
        ("CNCM - Centre national de création musicale", 8),
        ("CRC/CRI - Conservatoire à rayonnement communal ou intercommunal", 9),
        ("CRD - Conservatoire à rayonnement départemental", 10),
        ("CRR - Conservatoire à rayonnement régional", 11),
        ("FRAC - Fonds régional d'art contemporain", 12),
        ("Jardin remarquable", 13),
        ("LIR - Librairie indépendante de référence", 14),
        ("Maison des illustres", 15),
        ("Monuments historiques", 16),
        ("Musée de France", 17),
        ("Opéra national en région", 18),
        ("Orchestre national en région", 19),
        ("Patrimoine européen", 20),
        ("PNC - Pôle national du cirque", 21),
        ("Scène nationale", 22),
        ("Scènes conventionnées", 23),
        ("Sites patrimoniaux remarquables", 24),
        ("SMAC - Scène de musiques actuelles", 25),
        ("Théâtres nationaux", 26),
        ("UNESCO - Patrimoine mondial", 27),
        ("Ville et Pays d'art et d'histoire", 28),
        ("Théâtre lyrique conventionné d'intérêt national", 34),
        ("Centre Culturel de Rencontre", 35),
    ]

    save_new_venue_labels(venue_label_strings, sandbox)


def save_new_venue_labels(venue_label_strings: list[Tuple[str, int]], sandbox: bool = False) -> None:
    venue_label_list = []
    for label_string, label_id in venue_label_strings:
        venue_label = VenueLabel()
        if sandbox:
            venue_label.id = label_id
        venue_label.label = label_string
        venue_label_list.append(venue_label)
    repository.save(*venue_label_list)
