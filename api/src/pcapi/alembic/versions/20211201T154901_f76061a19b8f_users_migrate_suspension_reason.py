"""
Switch 'fraud' to 'fraud suspicion'
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "f76061a19b8f"
down_revision = "503904c2cab7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""UPDATE "user" SET "suspensionReason" = 'fraud suspicion' WHERE "user"."suspensionReason" = 'fraud'""")


def downgrade() -> None:
    op.execute("""UPDATE "user" SET "suspensionReason" = 'fraud' WHERE "user"."suspensionReason" = 'fraud suspicion'""")
