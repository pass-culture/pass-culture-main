"""Create spatial index for address table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "afe8049e9364"
down_revision = "3f2f6ae24d02"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.create_index(
        op.f("ix_address_geo_gist"),
        "address",
        [sa.text("(ST_MakePoint(longitude::double precision, latitude::double precision)::geography)")],
        if_not_exists=True,
        postgresql_using="gist",
        postgresql_concurrently=True,
        unique=False,
    )
    op.execute("BEGIN")


def downgrade() -> None:
    op.execute("COMMIT")
    op.drop_index(
        "ix_address_geo_gist",
        table_name="address",
        postgresql_concurrently=True,
        if_exists=True,
    )
    op.execute("BEGIN")
