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
    def as_dict(self):
        dict_value = {
            'type': 'Event',
            'value': str(self),
        }
        dict_value.update(self.value)
        return dict_value

    ACTIVATION = {
        'label': 'Pass Culture : activation évènementielle',
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': 'Activation',
        'description': 'Activez votre pass Culture grâce à cette offre',
        'conditionalFields': []
    }
    CINEMA = {
        'label': "Cinéma (Projections, Séances, Évènements)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?",
        'conditionalFields': ["author", "visa", "stageDirector"]
    }
    CONFERENCE_DEBAT_DEDICACE = {
        'label': "Conférence — Débat — Dédicace",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Rencontrer",
        'description': "Parfois une simple rencontre peut changer une vie...",
        'conditionalFields': ["speaker"]
    }
    JEUX = {
        'label': "Jeux (Évenements, Rencontres, Concours)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Jouer",
        'description': "Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?",
        'conditionalFields': []
    }
    MUSIQUE = {
        'label': "Musique (Concerts, Festivals)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Écouter",
        'description': "Plutôt rock, rap ou classique ? Sur un smartphone avec des écouteurs ou entre amis au concert ?",
        'conditionalFields': ["author", "musicType", "performer"]
    }
    MUSEES_PATRIMOINE = {
        'label': "Musées — Patrimoine (Expositions, Visites guidées, Activités spécifiques)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?",
        'conditionalFields': []
    }
    PRATIQUE_ARTISTIQUE = {
        'label': "Pratique Artistique (Stages ponctuels)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Pratiquer",
        'description': "Jamais osé monter sur les planches ? Tenter d’apprendre la guitare, le piano ou la photographie ? Partir cinq jours découvrir un autre monde ? Bricoler dans un fablab, ou pourquoi pas, enregistrer votre premier titre ?",
        'conditionalFields': ['speaker']
    }
    SPECTACLE_VIVANT = {
        'label': "Spectacle vivant",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Applaudir",
        'description': "Suivre un géant de 12 mètres dans la ville ? Rire aux éclats devant un stand up ? Rêver le temps d’un opéra ou d’un spectacle de danse ? Assister à une pièce de théâtre, ou se laisser conter une histoire ?",
        'conditionalFields': ["author", "showType", "stageDirector", "performer"]
    }


class ThingType(SearchableType):
    def as_dict(self):
        dict_value = {
            'type': 'Thing',
            'value': str(self),
        }
        dict_value.update(self.value)

        return dict_value

    ACTIVATION = {
        'label': 'Pass Culture : activation en ligne',
        'offlineOnly': False,
        'onlineOnly': True,
        'sublabel': 'Activation',
        'description': 'Activez votre pass Culture grâce à cette offre',
        'conditionalFields': []
    }
    AUDIOVISUEL = {
        'label': "Audiovisuel (Films sur supports physiques et VOD)",
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?",
        'conditionalFields': []
    }
    CINEMA_ABO = {
        'label': "Cinéma (Abonnements)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?",
        'conditionalFields': []
    }
    JEUX_ABO = {
        'label': "Jeux (Abonnements)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Jouer",
        'description': "Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?",
        'conditionalFields': []
    }
    JEUX = {
        'label': "Jeux (Biens physiques)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Jouer",
        'description': "Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?",
        'conditionalFields': []
    }
    JEUX_VIDEO = {
        'label': "Jeux Vidéo",
        'offlineOnly': False,
        'onlineOnly': True,
        'sublabel': "Jouer",
        'description': "Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?",
        'conditionalFields': []
    }
    LIVRE_EDITION = {
        'label': "Livre — Édition",
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': "Lire",
        'description': "S’abonner à un quotidien d’actualité ? À un hebdomadaire humoristique ? À un mensuel dédié à la nature ? Acheter une BD ou un manga ? Ou tout simplement ce livre dont tout le monde parle ?",
        'conditionalFields': ["author", "isbn"]
    }
    MUSEES_PATRIMOINE_ABO = {
        'label': "Musées — Patrimoine (Abonnements, Visites libres)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?",
        'conditionalFields': []
    }
    MUSIQUE_ABO = {
        'label': "Musique (Abonnements concerts)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Écouter",
        'description': "Plutôt rock, rap ou classique ? Sur un smartphone avec des écouteurs ou entre amis au concert ?",
        'conditionalFields': ["musicType"]
    }
    MUSIQUE = {
        'label': "Musique (sur supports physiques ou en ligne)",
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': "Écouter",
        'description': "Plutôt rock, rap ou classique ? Sur un smartphone avec des écouteurs ou entre amis au concert ?",
        'conditionalFields': ["author", "musicType", "performer"]
    }
    PRATIQUE_ARTISTIQUE_ABO = {
        'label': "Pratique Artistique (Abonnements)",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Pratiquer",
        'description': "Jamais osé monter sur les planches ? Tenter d’apprendre la guitare, le piano ou la photographie ? Partir cinq jours découvrir un autre monde ? Bricoler dans un fablab, ou pourquoi pas, enregistrer votre premier titre ?",
        'conditionalFields': ['speaker']
    }
    PRESSE_ABO = {
        'label': "Presse (Abonnements)",
        'offlineOnly': False,
        'onlineOnly': True,
        'sublabel': "Lire",
        'description': "S’abonner à un quotidien d’actualité ? À un hebdomadaire humoristique ? À un mensuel dédié à la nature ? Acheter une BD ou un manga ? Ou tout simplement ce livre dont tout le monde parle ?",
        'conditionalFields': []
    }


class ProductType:
    @classmethod
    def is_thing(cls, name: str) -> object:
        for possible_type in list(ThingType):
            if str(possible_type) == name:
                return True

        return False

    @classmethod
    def is_event(cls, name: str) -> object:
        for possible_type in list(EventType):
            if str(possible_type) == name:
                return True

        return False
