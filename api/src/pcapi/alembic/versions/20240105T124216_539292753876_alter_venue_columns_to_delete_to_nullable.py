"""Update fieldsUpdated column to be nullable before deletion."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "539292753876"
down_revision = "71effb72345c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "venue",
        "fieldsUpdated",
        existing_type=postgresql.ARRAY(sa.VARCHAR(length=100)),
        nullable=True,
    )


def downgrade() -> None:
    # This column is not used anymore we don't need to make it non-nullable
    pass
