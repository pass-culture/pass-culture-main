"""Alter table productMediation set fieldsUpdated nullable"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "88c4d806c740"
down_revision = "b409480c6113"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "product_mediation",
        "fieldsUpdated",
        existing_type=postgresql.ARRAY(sa.VARCHAR(length=100)),
        nullable=True,
        existing_server_default="{}",
    )


def downgrade() -> None:
    # If we would like to make this column non nullable,
    # we will have to manually do a migration since some empty data could have been inserted.
    # Since this column is unused it has no impact
    pass
