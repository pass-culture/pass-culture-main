""" model event """
from enum import Enum
from sqlalchemy import Binary,\
                       BigInteger,\
                       Boolean,\
                       Column,\
                       Index,\
                       Integer,\
                       String,\
                       Text,\
                       TEXT
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql.expression import cast, false
from sqlalchemy.sql.functions import coalesce

from models.db import Model
from models.deactivable_mixin import DeactivableMixin
from models.extra_data_mixin import ExtraDataMixin
from models.has_thumb_mixin import HasThumbMixin
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin
from utils.search import create_tsvector

class Accessibility(Enum):
    HEARING_IMPAIRED = 1
    VISUALLY_IMPAIRED = 2
    SIGN_LANGUAGE = 4
    MOTION_IMPAIRED = 8
    MENTALLY_IMPAIRED = 16


class EventType(Enum):
    CINEMA = {
        'label': "Cinéma (Projections, Séances, Évènements)", 'offlineOnly': True,
        'onlineOnly': False, 'sublabel': "Regarder"
    }
    CONFERENCE_DEBAT_DEDICACE = {
    'label': "Conférence — Débat — Dédicace", 'offlineOnly': True, 'onlineOnly': False, 'sublabel': "Rencontrer"
    }
    JEUX = {
    'label': "Jeux (Évenements, Rencontres, Concours)", 'offlineOnly': True, 'onlineOnly': False, 'sublabel': "Jouer"
    }
    MUSIQUE = {
    'label': "Musique (Concerts, Festivals)", 'offlineOnly': True, 'onlineOnly': False, 'sublabel': "Écouter"
    }
    MUSEES_PATRIMOINE = {
    'label': "Musées — Patrimoine (Expositions, Visites guidées, Activités spécifiques)", 'offlineOnly': True, 'onlineOnly': False, 'sublabel': "Regarder"
    }
    PRATIQUE_ARTISTIQUE = {
    'label': "Pratique Artistique (Stages ponctuels)", 'offlineOnly': True, 'onlineOnly': False, 'sublabel': "Pratiquer"
    }
    SPECTACLE_VIVANT = {
    'label': "Spectacle vivant", 'offlineOnly': True, 'onlineOnly': False, 'sublabel': "Applaudir"
    }


class Event(PcObject,
            Model,
            ExtraDataMixin,
            HasThumbMixin,
            ProvidableMixin
           ):
    id = Column(BigInteger,
                primary_key=True)

    type = Column(String(50),
                  nullable=True)

    name = Column(String(140), nullable=False)

    description = Column(Text, nullable=True)

    conditions = Column(String(120),
                        nullable=True)

    ageMin = Column(Integer,
                    nullable=True)
    ageMax = Column(Integer,
                    nullable=True)
    #TODO (from schema.org)
    #doorTime (datetime)
    #eventStatus
    #isAccessibleForFree (boolean)
    #typicalAgeRange → = $ageMin-$ageMax

    accessibility = Column(Binary(1),
                           nullable=False,
                           default=bytes([0]))

    mediaUrls = Column(ARRAY(String(220)),
                       nullable=False,
                       default=[])

    durationMinutes = Column(Integer,
                             nullable=False)

    isNational = Column(Boolean,
                        server_default=false(),
                        default=False,
                        nullable=False)

    @property
    def isDigital(self):
        return False

Event.__ts_vector__ = create_tsvector(
    cast(coalesce(Event.name, ''), TEXT)
)

Event.__table_args__ = (
    Index(
        'idx_event_fts',
        Event.__ts_vector__,
        postgresql_using='gin'
    ),
)
