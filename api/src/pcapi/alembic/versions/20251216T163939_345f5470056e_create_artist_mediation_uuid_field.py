"""create artist mediation_uuid field"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "345f5470056e"
down_revision = "4abc630a7f7c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("artist", sa.Column("mediation_uuid", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("artist", "mediation_uuid")
