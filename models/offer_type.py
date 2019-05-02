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
        'proLabel': 'Pass Culture : activation évènementielle',
        'appLabel': 'Pass Culture : activation évènementielle',
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': 'Activation',
        'description': 'Activez votre pass Culture grâce à cette offre',
        'conditionalFields': []
    }
    CINEMA = {
        'proLabel': "Cinéma — projections, séances, évènements",
        'appLabel': "Projections, Séances, Évènements",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?",
        'conditionalFields': ["author", "visa", "stageDirector"]
    }
    CONFERENCE_DEBAT_DEDICACE = {
        'proLabel': "Conférences, rencontres et découverte des métiers",
        'appLabel': "Conférences, rencontres et découverte des métiers",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Rencontrer",
        'description': "Parfois une simple rencontre peut changer une vie...",
        'conditionalFields': ["speaker"]
    }
    JEUX = {
        'proLabel': "Jeux — évenements, rencontres, concours",
        'appLabel': "Évenements, Rencontres, Concours",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Jouer",
        'description': "Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?",
        'conditionalFields': []
    }
    MUSIQUE = {
        'proLabel': "Musique — concerts, festivals",
        'appLabel': "Concerts, Festivals",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Écouter",
        'description': "Plutôt rock, rap ou classique ? Sur un smartphone avec des écouteurs ou entre amis au concert ?",
        'conditionalFields': ["author", "musicType", "performer"]
    }
    MUSEES_PATRIMOINE = {
        'proLabel': "Musées, patrimoine — expositions, visites guidées, activités spécifiques",
        'appLabel': "Expositions, visites guidées, activités spécifiques",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?",
        'conditionalFields': []
    }
    PRATIQUE_ARTISTIQUE = {
        'proLabel': "Pratique — séances d’essai et stages ponctuels",
        'appLabel': "Séances d’essai et stages ponctuels",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Pratiquer",
        'description': "Jamais osé monter sur les planches ? Tenter d’apprendre la guitare, le piano ou la photographie ? Partir cinq jours découvrir un autre monde ? Bricoler dans un fablab, ou pourquoi pas, enregistrer votre premier titre ?",
        'conditionalFields': ['speaker']
    }
    SPECTACLE_VIVANT = {
        'proLabel': "Spectacle vivant",
        'appLabel': "Spectacle vivant",
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
        'proLabel': 'Pass Culture : activation en ligne',
        'appLabel': 'Pass Culture : activation en ligne',
        'offlineOnly': False,
        'onlineOnly': True,
        'sublabel': 'Activation',
        'description': 'Activez votre pass Culture grâce à cette offre',
        'conditionalFields': []
    }
    AUDIOVISUEL = {
        'proLabel': "Audiovisuel — films sur supports physiques et VOD",
        'appLabel': "Films sur supports physiques et VOD",
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?",
        'conditionalFields': []
    }
    CINEMA_ABO = {
        'proLabel': "Cinéma — abonnements",
        'appLabel': "Abonnements",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?",
        'conditionalFields': []
    }
    JEUX = {
        'proLabel': "Jeux (support physique)",
        'appLabel': "Support physique",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Jouer",
        'description': "Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?",
        'conditionalFields': []
    }
    JEUX_VIDEO_ABO = {
        'proLabel': "Jeux — abonnements",
        'appLabel': "Jeux — abonnements",
        'offlineOnly': False,
        'onlineOnly': True,
        'sublabel': "Jouer",
        'description': "Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?",
        'conditionalFields': []
    }
    JEUX_VIDEO = {
        'proLabel': "Jeux vidéo",
        'appLabel': "Jeux vidéo",
        'offlineOnly': False,
        'onlineOnly': True,
        'sublabel': "Jouer",
        'description': "Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?",
        'conditionalFields': []
    }
    LIVRE_AUDIO = {
        'proLabel': "Livre audio numérique",
        'appLabel': "Livre audio numérique",
        'offlineOnly': False,
        'onlineOnly': True,
        'sublabel': "Lire",
        'description': "S’abonner à un quotidien d’actualité ? À un hebdomadaire humoristique ? À un mensuel dédié à la nature ? Acheter une BD ou un manga ? Ou tout simplement ce livre dont tout le monde parle ?",
        'conditionalFields': ["author"]
    }
    LIVRE_EDITION = {
        'proLabel': "Livre - format papier ou numérique, abonnements lecture",
        'appLabel': "Livres, cartes bibliothèque ou médiathèque",
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': "Lire",
        'description': "S’abonner à un quotidien d’actualité ? À un hebdomadaire humoristique ? À un mensuel dédié à la nature ? Acheter une BD ou un manga ? Ou tout simplement ce livre dont tout le monde parle ?",
        'conditionalFields': ["author", "isbn"]
    }
    MUSEES_PATRIMOINE_ABO = {
        'proLabel': "Musées, arts visuels & patrimoine",
        'appLabel': "Visites libres et abonnements",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?",
        'conditionalFields': []
    }
    MUSIQUE_ABO = {
        'proLabel': "Musique — abonnements concerts",
        'appLabel': "Abonnements concerts",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Écouter",
        'description': "Plutôt rock, rap ou classique ? Sur un smartphone avec des écouteurs ou entre amis au concert ?",
        'conditionalFields': ["musicType"]
    }
    MUSIQUE = {
        'proLabel': "Musique (sur supports physiques ou en ligne)",
        'appLabel': "Supports physiques ou en ligne",
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': "Écouter",
        'description': "Plutôt rock, rap ou classique ? Sur un smartphone avec des écouteurs ou entre amis au concert ?",
        'conditionalFields': ["author", "musicType", "performer"]
    }
    OEUVRE_ART = {
        'proLabel': "Vente d'œuvres d'art",
        'appLabel': "Achat d'œuvres d’art",
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?",
        'conditionalFields': []
    }
    PRATIQUE_ARTISTIQUE_ABO = {
        'proLabel': "Pratique artistique — abonnements",
        'appLabel': "Pratique artistique — abonnements",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Pratiquer",
        'description': "Jamais osé monter sur les planches ? Tenter d’apprendre la guitare, le piano ou la photographie ? Partir cinq jours découvrir un autre monde ? Bricoler dans un fablab, ou pourquoi pas, enregistrer votre premier titre ?",
        'conditionalFields': ['speaker']
    }
    PRESSE_ABO = {
        'proLabel': "Presse — Abonnements",
        'appLabel': "Presse — Abonnements",
        'offlineOnly': False,
        'onlineOnly': True,
        'sublabel': "Lire",
        'description': "S’abonner à un quotidien d’actualité ? À un hebdomadaire humoristique ? À un mensuel dédié à la nature ? Acheter une BD ou un manga ? Ou tout simplement ce livre dont tout le monde parle ?",
        'conditionalFields': []
    }
    INSTRUMENT = {
        'proLabel': "Vente d’instruments de musique",
        'appLabel': "Achat d’instruments de musique",
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': "Pratiquer",
        'description': "Jamais osé monter sur les planches ? Tenter d’apprendre la guitare, le piano ou la photographie ? Partir cinq jours découvrir un autre monde ? Bricoler dans un fablab, ou pourquoi pas, enregistrer votre premier titre ?",
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
