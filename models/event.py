""" model event """
from enum import Enum
from flask_sqlalchemy import Model
from sqlalchemy import Binary,\
                       BigInteger,\
                       Boolean,\
                       Column,\
                       Integer,\
                       String,\
                       Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql.expression import false

from models.deactivable_mixin import DeactivableMixin
from models.extra_data_mixin import ExtraDataMixin
from models.has_thumb_mixin import HasThumbMixin
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin

class Accessibility(Enum):
    HEARING_IMPAIRED = 1
    VISUALLY_IMPAIRED = 2
    SIGN_LANGUAGE = 4
    MOTION_IMPAIRED = 8
    MENTALLY_IMPAIRED = 16


class EventType(Enum):
    Workshop          = "Cours ou atelier de pratique artistique, bal..."
    MovieScreening    = "Cinéma / Projection de film"
    Meeting           = "Dédicace / Rencontre / Conférence"
    Game              = "Jeu / Concours / Tournoi"
    SchoolHelp        = "Soutien scolaire"
    StreetPerformance = "Arts de la rue"
    Other             = "Autres"
    BookReading       = "Lecture"
    CircusAndMagic    = "Cirque / Magie"
    DancePerformance  = "Danse"
    Comedy            = "Humour / Café-théâtre"
    Concert           = "Concert"
    Combo             = "Pluridisciplinaire"
    Youth             = "Spectacle Jeunesse"
    Musical           = "Spectacle Musical / Cabaret / Opérette"
    Theater           = "Théâtre"
    GuidedVisit       = "Visite guidée : Exposition, Musée, Monument..."
    FreeVisit         = "Visite libre : Exposition, Musée, Monument..."


EventType = EventType




class Event(PcObject,
            Model,
            DeactivableMixin,
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
