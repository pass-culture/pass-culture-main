from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declared_attr
import sqlalchemy.orm as sa_orm


if TYPE_CHECKING:
    from pcapi.core.providers.models import Provider


@sa_orm.declarative_mixin
class ProvidableMixin:
    @declared_attr
    def lastProviderId(cls) -> sa_orm.Mapped[int | None]:  # pylint: disable=no-self-argument
        return sa.Column(sa.BigInteger, sa.ForeignKey("provider.id"), nullable=True)

    @declared_attr
    def lastProvider(cls) -> sa_orm.Mapped["Provider | None"]:  # pylint: disable=no-self-argument
        return sa_orm.relationship("Provider", foreign_keys=[cls.lastProviderId])

    idAtProviders = sa.Column(
        sa.String(70),
        sa.CheckConstraint(
            '"lastProviderId" IS NULL OR "idAtProviders" IS NOT NULL',
            name="check_providable_with_provider_has_idatproviders",
        ),
        nullable=True,
        unique=True,
    )

    dateModifiedAtLastProvider = sa.Column(sa.DateTime, nullable=True, default=datetime.utcnow)

    fieldsUpdated: sa_orm.Mapped[list[str]] = sa.Column(
        ARRAY(sa.String(100)), nullable=False, default=[], server_default="{}"
    )
