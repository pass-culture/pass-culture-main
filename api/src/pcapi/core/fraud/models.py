import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


if TYPE_CHECKING:
    from pcapi.core.users.models import User


class BlacklistedDomainName(PcObject, Base, Model):
    """
    Track all blacklisted domain names. Any account creation or update
    using an email from one of those domain names should be blocked.

    To get more context, seek for the corresponding action that has been
    logged inside the action_history table.
    """

    __tablename__ = "blacklisted_domain_name"
    domain: str = sa.Column(sa.Text, nullable=False, unique=True)
    dateCreated: datetime.datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.datetime.utcnow, server_default=sa.func.now()
    )


class ProductWhitelist(PcObject, Base, Model):
    """
    Contains the whitelisted EAN
    """

    __tablename__ = "product_whitelist"
    title: str = sa.Column(sa.Text, nullable=False)
    ean: str = sa.Column(sa.String(length=13), nullable=False, unique=True, index=True)
    dateCreated: datetime.datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.datetime.utcnow, server_default=sa.func.now()
    )
    comment: str = sa.Column(sa.Text, nullable=False)
    authorId: int = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=False)
    author: sa_orm.Mapped["User"] = sa_orm.relationship("User", foreign_keys=[authorId])
