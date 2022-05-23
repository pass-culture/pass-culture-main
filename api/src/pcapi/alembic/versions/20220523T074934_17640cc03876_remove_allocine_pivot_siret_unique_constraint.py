"""remove allocine_pivot unique constraint on siret
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "17640cc03876"
down_revision = "4400cd98902e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("allocine_pivot_siret_key", "allocine_pivot", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint("allocine_pivot_siret_key", "allocine_pivot", ["siret"])
