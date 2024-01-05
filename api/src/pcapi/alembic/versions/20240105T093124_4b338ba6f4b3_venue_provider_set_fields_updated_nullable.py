"""Update venueProvider.fieldsUpdated to be nullable before deletion."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "4b338ba6f4b3"
down_revision = "ea44e2105865"
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
    # this column will be set not nullable by fc57ac28e117 post downgrade
    pass
