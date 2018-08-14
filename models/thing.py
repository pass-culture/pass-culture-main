""" thing model """
import enum
from sqlalchemy import BigInteger,\
                       CheckConstraint,\
                       Column,\
                       Index,\
                       String,\
                       Text
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.functions import coalesce

from models.db import Model
from models.deactivable_mixin import DeactivableMixin
from models.extra_data_mixin import ExtraDataMixin
from models.has_thumb_mixin import HasThumbMixin
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin
from utils.search import create_tsvector


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

    url = Column(String(255), nullable=True)

    @property
    def isDigital(self):
        return self.url is not None and self.url != ''


Thing.__ts_vector__ = create_tsvector(
    cast(coalesce(Thing.name, ''), TEXT),
    coalesce(Thing.extraData['author'].cast(TEXT), ''),
    coalesce(Thing.extraData['byArtist'].cast(TEXT), ''),
)

Thing.__table_args__ = (
    Index(
        'idx_thing_fts',
        Thing.__ts_vector__,
        postgresql_using='gin'
    ),
)
