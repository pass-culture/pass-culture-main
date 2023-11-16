"""add formats to validation attributes"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "f81aecdc3793"
down_revision = "705d56381bae"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE offer_validation_attribute ADD VALUE IF NOT EXISTS 'FORMATS'")
    op.execute("ALTER TYPE offer_validation_rule_operator ADD VALUE IF NOT EXISTS 'INTERSECTS'")
    op.execute("ALTER TYPE offer_validation_rule_operator ADD VALUE IF NOT EXISTS 'NOT_INTERSECTS'")


def downgrade() -> None:
    pass
