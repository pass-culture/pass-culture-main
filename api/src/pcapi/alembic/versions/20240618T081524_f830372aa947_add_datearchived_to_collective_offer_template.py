"""
Add "dateArchived" column to "collective_offer_template" table.
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "f830372aa947"
down_revision = "3e52841cdafa"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("collective_offer_template", sa.Column("dateArchived", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("collective_offer_template", "dateArchived")
