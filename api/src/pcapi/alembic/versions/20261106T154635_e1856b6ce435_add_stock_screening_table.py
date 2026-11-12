"""Add stock screening table"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from pcapi.core.offers import constants as offers_constants
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "e1856b6ce435"
down_revision = "224c7a7ce18d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "screening",
        sa.Column("stockId", sa.BigInteger(), nullable=False),
        sa.Column("language", MagicEnum(offers_constants.LanguageFeatures), nullable=True),
        sa.Column("videoFormat", MagicEnum(offers_constants.VideoFeatures), nullable=True),
        sa.Column("accessibility", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("specialEventType", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(["stockId"], ["stock.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("screening")
