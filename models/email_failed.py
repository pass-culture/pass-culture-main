from datetime import datetime
from sqlalchemy import Column, BigInteger, String, DateTime, JSON

from models.db import Model
from models.pc_object import PcObject


class EmailFailed(PcObject,
                  Model,
                  ):
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)
    json = Column(JSON,
                  nullable=False)
    status = Column(String(12),
                    nullable=False)

    datetime = Column(DateTime,
                      nullable=False,
                      default=datetime.utcnow)
