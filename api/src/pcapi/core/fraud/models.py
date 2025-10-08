import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.models import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils import date as date_utils


if TYPE_CHECKING:
    from pcapi.core.users.models import User


class BlacklistedDomainName(PcObject, Model):
    """
    Track all blacklisted domain names. Any account creation or update
    using an email from one of those domain names should be blocked.

    To get more context, seek for the corresponding action that has been
    logged inside the action_history table.
    """

    __tablename__ = "blacklisted_domain_name"
    domain: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False, unique=True)
    dateCreated: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now, server_default=sa.func.now()
    )


class ProductWhitelist(PcObject, Model):
    """
    Contains the whitelisted EAN
    """

    __tablename__ = "product_whitelist"
    title: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)
    ean: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(length=13), nullable=False, unique=True, index=True)
    dateCreated: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=date_utils.get_naive_utc_now, server_default=sa.func.now()
    )
    comment: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)
    authorId: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger, sa.ForeignKey("user.id"), nullable=False)
    author: sa_orm.Mapped["User"] = sa_orm.relationship("User", foreign_keys=[authorId])
