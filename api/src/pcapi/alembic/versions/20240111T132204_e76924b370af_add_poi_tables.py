"""Add POI tables
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "e76924b370af"
down_revision = "025c622f64f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "address",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("banId", sa.Text(), nullable=True),
        sa.Column("street", sa.Text(), nullable=False),
        sa.Column("postalCode", sa.String(length=10), nullable=False),
        sa.Column("city", sa.String(length=50), nullable=False),
        sa.Column("country", sa.String(length=50), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=8, scale=5), nullable=False),
        sa.Column("longitude", sa.Numeric(precision=8, scale=5), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("banId"),
    )
    op.create_index(
        "ix_unique_address_per_banid",
        "address",
        ["banId"],
        unique=True,
        postgresql_where=sa.text('"banId" IS NOT NULL'),
    )
    op.create_index(
        "ix_unique_address_per_street_and_postalcode",
        "address",
        ["street", "postalCode"],
        unique=True,
        postgresql_where=sa.text('"banId" IS NULL'),
    )
    op.create_table(
        "point_of_interest",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("audioDisabilityCompliant", sa.Boolean(), nullable=True),
        sa.Column("mentalDisabilityCompliant", sa.Boolean(), nullable=True),
        sa.Column("motorDisabilityCompliant", sa.Boolean(), nullable=True),
        sa.Column("visualDisabilityCompliant", sa.Boolean(), nullable=True),
        sa.Column("extraAddress", sa.Text(), nullable=True),
        sa.Column("addressId", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["addressId"],
            ["address.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_unique_poi_per_address_and_extra_address",
        "point_of_interest",
        ["extraAddress", "addressId"],
        unique=True,
        postgresql_where=sa.text('"extraAddress" IS NOT NULL'),
    )
    op.create_table(
        "offerer_point_of_interest",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("pointOfInterestId", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["pointOfInterestId"],
            ["point_of_interest.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("offerer_point_of_interest")
    op.drop_index(
        "ix_unique_poi_per_address_and_extra_address",
        table_name="point_of_interest",
        postgresql_where=sa.text('"extraAddress" IS NOT NULL'),
    )
    op.drop_table("point_of_interest")
    op.drop_index(
        "ix_unique_address_per_street_and_postalcode", table_name="address", postgresql_where=sa.text('"banId" IS NULL')
    )
    op.drop_index("ix_unique_address_per_banid", table_name="address", postgresql_where=sa.text('"banId" IS NOT NULL'))
    op.drop_table("address")
