""" thing model """
import enum

from sqlalchemy import BigInteger, \
    CheckConstraint, \
    Column, \
    Index, \
    String, \
    Text, Boolean
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.functions import coalesce

from models.offer_type import ThingType
from models.db import Model
from models.extra_data_mixin import ExtraDataMixin
from models.has_thumb_mixin import HasThumbMixin
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin
from domain.search import create_tsvector


class BookFormat(enum.Enum):
    AudiobookFormat = "AudiobookFormat"
    EBook = "EBook"
    Hardcover = "Hardcover"
    Paperback = "Paperback"


class Thing(PcObject,
            Model,
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

    isNational = Column(Boolean,
                        default=False,
                        nullable=False)

    @property
    def enum_type(self):
        for possible_type in list(ThingType):
            if str(possible_type) == self.type:
                return possible_type
        return self.type

    @property
    def isDigital(self):
        return self.url is not None and self.url != ''

    def _type_can_only_be_offline(self):
        offline_only_things = filter(lambda thing_type: thing_type.value['offlineOnly'], ThingType)
        offline_only_types_for_things = map(lambda x: x.__str__(), offline_only_things)
        return self.type in offline_only_types_for_things

    def _get_label_from_type_string(self):
        matching_type_thing = next(filter(lambda thing_type: thing_type.__str__() == self.type, ThingType))
        return matching_type_thing.value['label']

    def errors(self):
        api_errors = super(Thing, self).errors()
        if self.isDigital and self._type_can_only_be_offline():
            api_errors.addError('url', 'Une offre de type {} ne peut pas être numérique'.format(
                self._get_label_from_type_string()))
        return api_errors


Thing.__ts_vector__ = create_tsvector(
    cast(coalesce(Thing.name, ''), TEXT),
    coalesce(Thing.extraData['author'].cast(TEXT), ''),
    coalesce(Thing.extraData['byArtist'].cast(TEXT), ''),
    cast(coalesce(Thing.description, ''), TEXT),
)

Thing.__table_args__ = (
    Index(
        'idx_thing_fts',
        Thing.__ts_vector__,
        postgresql_using='gin'
    ),
)
