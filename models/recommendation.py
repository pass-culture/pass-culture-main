from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, and_, exists
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.sql import expression, select

from models.db import Model
from models.favorite_sql_entity import FavoriteSQLEntity
from models.pc_object import PcObject


class Recommendation(PcObject, Model):
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    userId = Column(BigInteger,
                    ForeignKey('user.id'),
                    nullable=False,
                    index=True)

    user = relationship('UserSQLEntity',
                        foreign_keys=[userId],
                        backref='recommendations')

    mediationId = Column(BigInteger,
                         ForeignKey('mediation.id'),
                         index=True,
                         nullable=True)  # NULL for recommendation created directly from a thing or an event

    mediation = relationship('Mediation',
                             foreign_keys=[mediationId],
                             backref='recommendations')

    offerId = Column(BigInteger,
                     ForeignKey('offer.id'),
                     index=True,
                     nullable=True)

    offer = relationship('Offer',
                         foreign_keys=[offerId],
                         backref='recommendations')

    shareMedium = Column(String(20),
                         nullable=True)

    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    dateUpdated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    dateRead = Column(DateTime,
                      nullable=True)

    isClicked = Column(Boolean,
                       nullable=False,
                       server_default=expression.false(),
                       default=False)

    isFirst = Column(Boolean,
                     nullable=False,
                     server_default=expression.false(),
                     default=False)

    search = Column(String,
                    nullable=True)

    isFavorite = column_property(
        exists(select([FavoriteSQLEntity.id]).
               where(and_(userId == FavoriteSQLEntity.userId,
                          (offerId == FavoriteSQLEntity.offerId))
                     )
               ))

    @property
    def thumbUrl(self) -> str:
        if self.mediationId:
            return self.mediation.thumbUrl

        return self.offer.product.thumbUrl
