from enum import Enum


class SearchableType(Enum):
    @classmethod
    def find_from_sub_labels(cls, sub_labels):
        matching_types = []
        comparable_sub_labels = [label.lower() for label in sub_labels]

        for type in cls:
            if type.value['sublabel'].lower() in comparable_sub_labels:
                matching_types.append(type)

        return matching_types


class EventType(SearchableType):
    CINEMA = {
        'label': "Cinéma (Projections, Séances, Évènements)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Example"
    }
    CONFERENCE_DEBAT_DEDICACE = {
        'label': "Conférence — Débat — Dédicace",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Rencontrer",
        'description': "Example"
    }
    JEUX = {
        'label': "Jeux (Évenements, Rencontres, Concours)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Jouer",
        'description': "Example"
    }
    MUSIQUE = {
        'label': "Musique (Concerts, Festivals)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Écouter",
        'description': "Example"
    }
    MUSEES_PATRIMOINE = {
        'label': "Musées — Patrimoine (Expositions, Visites guidées, Activités spécifiques)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Example"
    }
    PRATIQUE_ARTISTIQUE = {
        'label': "Pratique Artistique (Stages ponctuels)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Pratiquer",
        'description': "Example"
    }
    SPECTACLE_VIVANT = {
        'label': "Spectacle vivant",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Applaudir",
        'description': "Example"
    }


class ThingType(SearchableType):
    AUDIOVISUEL = {
        'label': "Audiovisuel (Films sur supports physiques et VOD)",
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Example"
    }
    CINEMA_ABO = {
        'label': "Cinéma (Abonnements)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Example"
    }
    JEUX_ABO = {
        'label': "Jeux (Abonnements)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Jouer",
        'description': "Example"
    }
    JEUX = {
        'label': "Jeux (Biens physiques)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Jouer",
        'description': "Example"
    }
    JEUX_VIDEO = {
        'label': "Jeux Vidéo",
        'offlineOnly': False,
        'onlineOnly': True,
        'sublabel': "Jouer",
        'description': "Example"
    }
    LIVRE_EDITION = {
        'label': "Livre — Édition",
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': "Lire",
        'description': "Example"
    }
    MUSEES_PATRIMOINE_ABO = {
        'label': "Musées — Patrimoine (Abonnements, Visites libres)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Example"
    }
    MUSIQUE_ABO = {
        'label': "Musique (Abonnements concerts)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Écouter",
        'description': "Example"
    }
    MUSIQUE = {
        'label': "Musique (sur supports physiques ou en ligne)",
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': "Écouter",
        'description': "Example"
    }
    PRATIQUE_ARTISTIQUE_ABO = {
        'label': "Pratique Artistique (Abonnements)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Pratiquer",
        'description': "Example"
    }
    PRESSE_ABO = {
        'label': "Presse (Abonnements)",
        'offlineOnly': False,
        'onlineOnly': True,
        'sublabel': "Lire",
        'description': "Example"
    }
