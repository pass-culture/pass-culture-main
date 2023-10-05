"""
Create_iris_table to handle anonymous localisation and conforming to RGPD
"""
from alembic import op
import geoalchemy2
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "76c6f21e2f24"
down_revision = "4205ae20bb32"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "iris_france",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=9), nullable=False),
        sa.Column(
            "shape",
            geoalchemy2.types.Geometry(srid=4326, from_text="ST_GeomFromEWKT", name="geometry", nullable=False),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )


def downgrade() -> None:
    op.drop_index("idx_iris_france_shape", table_name="iris_france", postgresql_using="gist")
    op.drop_table("iris_france")
