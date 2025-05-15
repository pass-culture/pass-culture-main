"""Drop fieldsUpdated column from product"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1eb6460032d1"
down_revision = "2d9c4b59ac7c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("product", "fieldsUpdated")


def downgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.add_column(
        "product",
        sa.Column(
            "fieldsUpdated",
            postgresql.ARRAY(sa.VARCHAR(length=100)),
            server_default=sa.text("'{}'::character varying[]"),
            autoincrement=False,
            nullable=True,
        ),
    )
