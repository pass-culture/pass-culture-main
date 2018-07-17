""" thing model """
import enum
from flask_sqlalchemy import Model
from sqlalchemy import BigInteger,\
                       CheckConstraint,\
                       Column,\
                       Index,\
                       String,\
                       Text
from sqlalchemy.dialects.postgresql import ARRAY, TEXT

from models.deactivable_mixin import DeactivableMixin
from models.extra_data_mixin import ExtraDataMixin
from models.has_thumb_mixin import HasThumbMixin
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin


class BookFormat(enum.Enum):
    AudiobookFormat = "AudiobookFormat"
    EBook = "EBook"
    Hardcover = "Hardcover"
    Paperback = "Paperback"


class ThingType(enum.Enum):
    Book = "Livre"
#    CD = "CD"
#    Vinyl = "Vinyle"
#    StreamingMusicSubscription = "Musique en streaming"
#    MusicDownload = "Musique en téléchargement"
#    Bluray = "Bluray"
#    DVD = "DVD"
#    VOD = "VOD"


class Thing(PcObject,
            Model,
            DeactivableMixin,
            HasThumbMixin,
            ProvidableMixin,
            ExtraDataMixin):

    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    type = Column(String(50),
                  CheckConstraint("\"type\" <> 'Book' OR \"extraData\"->>'prix_livre' SIMILAR TO '[0-9]+(.[0-9]*|)'",
                                        name='check_thing_book_has_price'),
                  CheckConstraint("\"type\" <> 'Book' OR NOT \"extraData\"->'author' IS NULL",
                                        name='check_thing_book_has_author'),
                  CheckConstraint("\"type\" <> 'Book' OR \"idAtProviders\" SIMILAR TO '[0-9]{13}'",
                                        name='check_thing_book_has_ean13'),
                  nullable=False)

    name = Column(String(140), nullable=False)

    description = Column(Text, nullable=True)

    mediaUrls = Column(ARRAY(String(120)),
                          nullable=False,
                          default=[])
