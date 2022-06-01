"""remove_not_null_siret_on_allocine_pivot
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "dd318872da8d"
down_revision = "16ce9f750e7c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE allocine_pivot ALTER COLUMN siret DROP NOT NULL;")


def downgrade() -> None:
    op.execute("ALTER TABLE allocine_pivot ALTER COLUMN siret SET NOT NULL;")
