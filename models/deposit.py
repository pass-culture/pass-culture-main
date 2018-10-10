from sqlalchemy import Column, BigInteger, Numeric, String, ForeignKey
from sqlalchemy.orm import relationship

from models.pc_object import PcObject
from models.has_thumb_mixin import  HasThumbMixin
from models.db import Model


class Deposit(PcObject,
                Model,
              ):
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)
    amount = Column(Numeric(10, 2),
                   nullable=False)
    userId = Column(BigInteger,
                    ForeignKey('user.id'),
                    index=True,
                    nullable=False)

    user = relationship('User',
                        foreign_keys=[userId],
                        backref='deposits')
    source = Column(String(12),
                   nullable=False)
