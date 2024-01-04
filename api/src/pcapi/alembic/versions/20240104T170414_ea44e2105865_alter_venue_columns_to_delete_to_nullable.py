"""Update fieldsUpdated column to be nullable before deletion."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ea44e2105865"
down_revision = "ea0a25aef628"
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
    # this column will be set not nullable by fc57ac28e117 post downgrade
    pass
