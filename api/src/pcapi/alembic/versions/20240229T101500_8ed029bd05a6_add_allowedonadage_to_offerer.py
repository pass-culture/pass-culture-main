"""add allowedOnAdage to Offerer"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "8ed029bd05a6"
down_revision = "df028bd09c15"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""ALTER TABLE offerer ADD COLUMN IF NOT EXISTS "allowedOnAdage" BOOLEAN DEFAULT false NOT NULL;""")


def downgrade() -> None:
    op.execute("""ALTER TABLE offerer DROP COLUMN IF EXISTS "allowedOnAdage";""")
