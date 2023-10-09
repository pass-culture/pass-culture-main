"""Alter table offerer set unused columns nullable."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "695bc13a7be4"
down_revision = "76c6f21e2f24"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("offerer", "thumbCount", existing_type=sa.INTEGER(), nullable=True)
    op.alter_column(
        "offerer",
        "fieldsUpdated",
        existing_type=postgresql.ARRAY(sa.VARCHAR(length=100)),
        nullable=True,
        existing_server_default=sa.text("'{}'::character varying[]"),
    )


def downgrade() -> None:
    # these columns will be set not nullable by cd2fcba2f97f post downgrade
    pass
