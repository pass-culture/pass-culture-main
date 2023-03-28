"""permit_null_expiration_date
"""
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1b9fe434199c"
down_revision = "d1eb4e7db641"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("collective_dms_application", "expirationDate", existing_type=postgresql.TIMESTAMP(), nullable=True)


def downgrade() -> None:
    op.alter_column(
        "collective_dms_application", "expirationDate", existing_type=postgresql.TIMESTAMP(), nullable=False
    )
