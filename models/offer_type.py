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
        'sublabel': "Regarder"
    }
    CONFERENCE_DEBAT_DEDICACE = {
        'label': "Conférence — Débat — Dédicace",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Rencontrer"
    }
    JEUX = {
        'label': "Jeux (Évenements, Rencontres, Concours)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Jouer"
    }
    MUSIQUE = {
        'label': "Musique (Concerts, Festivals)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Écouter"
    }
    MUSEES_PATRIMOINE = {
        'label': "Musées — Patrimoine (Expositions, Visites guidées, Activités spécifiques)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Regarder"
    }
    PRATIQUE_ARTISTIQUE = {
        'label': "Pratique Artistique (Stages ponctuels)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Pratiquer"
    }
    SPECTACLE_VIVANT = {
        'label': "Spectacle vivant",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Applaudir"
    }


class ThingType(SearchableType):
    AUDIOVISUEL = {
        'label': "Audiovisuel (Films sur supports physiques et VOD)",
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': "Regarder"
    }
    CINEMA_ABO = {
        'label': "Cinéma (Abonnements)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Regarder"
    }
    JEUX_ABO = {
        'label': "Jeux (Abonnements)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Jouer"
    }
    JEUX = {
        'label': "Jeux (Biens physiques)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Jouer"
    }
    JEUX_VIDEO = {
        'label': "Jeux Vidéo",
        'offlineOnly': False,
        'onlineOnly': True,
        'sublabel': "Jouer"
    }
    LIVRE_EDITION = {
        'label': "Livre — Édition",
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': "Lire"
    }
    MUSEES_PATRIMOINE_ABO = {
        'label': "Musées — Patrimoine (Abonnements, Visites libres)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Regarder"
    }
    MUSIQUE_ABO = {
        'label': "Musique (Abonnements concerts)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Écouter"
    }
    MUSIQUE = {
        'label': "Musique (sur supports physiques ou en ligne)",
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': "Écouter"
    }
    PRATIQUE_ARTISTIQUE_ABO = {
        'label': "Pratique Artistique (Abonnements)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Pratiquer"
    }
    PRESSE_ABO = {
        'label': "Presse (Abonnements)",
        'offlineOnly': False,
        'onlineOnly': True,
        'sublabel': "Lire"
    }
