import enum
from flask import current_app as app
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.dialects.postgresql import JSON

from utils.schema_org import make_schema_org_hierarchy_and_enum
from utils.search import create_tsvector

db = app.db


class BookFormat(enum.Enum):
    AudiobookFormat = "AudiobookFormat"
    EBook = "EBook"
    Hardcover = "Hardcover"
    Paperback = "Paperback"


app.model.BookFormat = BookFormat


class ThingType(enum.Enum):
    Book = "Livre"
#    CD = "CD"
#    Vinyl = "Vinyle"
#    StreamingMusicSubscription = "Musique en streaming"
#    MusicDownload = "Musique en téléchargement"
#    Bluray = "Bluray"
#    DVD = "DVD"
#    VOD = "VOD"


app.model.ThingType = ThingType


class Thing(app.model.PcObject,
           db.Model,
           app.model.DeactivableMixin,
           app.model.HasThumbMixin,
           app.model.ProvidableMixin,
           app.model.ExtraDataMixin):

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


app.model.Thing = Thing
