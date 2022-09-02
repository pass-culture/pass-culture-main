from uuid import UUID

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_psql

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class UserSession(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    userId = sa.Column(sa.BigInteger, nullable=False)

    uuid: UUID = sa.Column(sa_psql.UUID(as_uuid=True), unique=True, nullable=False)
