"""Update venueProvider.fieldsUpdated to be nullable before deletion."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1fb084a51b0d"
down_revision = "539292753876"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "venue_provider",
        "fieldsUpdated",
        existing_type=postgresql.ARRAY(sa.VARCHAR(length=100)),
        nullable=True,
    )


def downgrade() -> None:
    # This column is not used anymore we don't need to make it non-nullable
    pass
