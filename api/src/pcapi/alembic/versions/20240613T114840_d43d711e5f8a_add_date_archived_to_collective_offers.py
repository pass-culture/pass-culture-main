"""
Add "dateArchived" column to "collective_offer" table.
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d43d711e5f8a"
down_revision = "a909ecd976dc"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("collective_offer", sa.Column("dateArchived", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("collective_offer", "dateArchived")
