"""Add user.validatedBirthDate column
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "685f32d7cb22"
down_revision = "d19b9f8cf4d0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""ALTER TABLE "user" ADD COLUMN IF NOT EXISTS "validatedBirthDate" DATE;""")


def downgrade() -> None:
    op.drop_column("user", "validatedBirthDate")
