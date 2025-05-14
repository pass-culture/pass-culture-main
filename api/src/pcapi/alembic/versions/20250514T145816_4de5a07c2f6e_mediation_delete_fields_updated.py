"""Drop fieldsUpdated column from mediation"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4de5a07c2f6e"
down_revision = "c8fe4d1d4771"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("mediation", "fieldsUpdated")


def downgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.add_column(
        "mediation",
        sa.Column(
            "fieldsUpdated",
            postgresql.ARRAY(sa.VARCHAR(length=100)),
            server_default=sa.text("'{}'::character varying[]"),
            autoincrement=False,
            nullable=True,
        ),
    )
