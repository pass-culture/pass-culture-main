"""Add Nature/Format/Domain to Offer"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.nature_format_domain import nature_format_domain as nfd
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ebf2d4fcbd43"
down_revision = "224c7a7ce18d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("offer", sa.Column("nature", MagicEnum(nfd.NatureEnum), nullable=True))
    op.add_column("offer", sa.Column("format", MagicEnum(nfd.FormatEnum), nullable=True))
    op.add_column("offer", sa.Column("domaine", MagicEnum(nfd.DomainEnum), nullable=True))


def downgrade() -> None:
    op.drop_column("offer", "domaine")
    op.drop_column("offer", "format")
    op.drop_column("offer", "nature")
