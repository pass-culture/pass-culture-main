"""Drop address of the offerer: street, postalCode, city"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f2c8dc495880"
down_revision = "67509f8bb41b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("offerer", "postalCode")
    op.drop_column("offerer", "address")
    op.drop_column("offerer", "city")


def downgrade() -> None:
    op.add_column("offerer", sa.Column("city", sa.Text, autoincrement=False, nullable=True))
    op.add_column("offerer", sa.Column("address", sa.Text, autoincrement=False, nullable=True))
    op.add_column("offerer", sa.Column("postalCode", sa.Text, autoincrement=False, nullable=True))
