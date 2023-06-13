"""ADD features column to stock table"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "df422d433b32"
down_revision = "893524dbab24"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE stock ADD COLUMN IF NOT EXISTS features TEXT[] DEFAULT '{}'::text[] NOT NULL")


def downgrade() -> None:
    op.drop_column("stock", "features")
