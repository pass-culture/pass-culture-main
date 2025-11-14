"""add column wikidata_id to artist table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "62fa496efa1b"
down_revision = "adc893f296c4"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("artist", sa.Column("wikidata_id", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("artist", "wikidata_id")
