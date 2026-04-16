"""create table cultural_outreach"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.cultural_outreach.models import CulturalOutreachStatus
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "de0fbd846d9f"
down_revision = "4c0c60c2ab7d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cultural_outreach",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=False),
        sa.Column("claimedDatetime", sa.DateTime(), nullable=True),
        sa.Column(
            "status",
            MagicEnum(CulturalOutreachStatus),
            nullable=False,
            server_default=CulturalOutreachStatus.PENDING.value,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("cultural_outreach", if_exists=True)
