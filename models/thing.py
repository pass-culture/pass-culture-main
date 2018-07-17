import enum

import sqlalchemy as db
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.functions import coalesce

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
            db.Model,
            DeactivableMixin,
            HasThumbMixin,
            ProvidableMixin,
            ExtraDataMixin):

    id = db.Column(db.BigInteger,
                   primary_key=True,
                   autoincrement=True)

    type = db.Column(db.String(50),
                     db.CheckConstraint("\"type\" <> 'Book' OR \"extraData\"->>'prix_livre' SIMILAR TO '[0-9]+(.[0-9]*|)'",
                                        name='check_thing_book_has_price'),
                     db.CheckConstraint("\"type\" <> 'Book' OR NOT \"extraData\"->'author' IS NULL",
                                        name='check_thing_book_has_author'),
                     db.CheckConstraint("\"type\" <> 'Book' OR \"idAtProviders\" SIMILAR TO '[0-9]{13}'",
                                        name='check_thing_book_has_ean13'),
                     nullable=False)

    name = db.Column(db.String(140), nullable=False)

    description = db.Column(db.Text, nullable=True)

    mediaUrls = db.Column(ARRAY(db.String(120)),
                          nullable=False,
                          default=[])


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
