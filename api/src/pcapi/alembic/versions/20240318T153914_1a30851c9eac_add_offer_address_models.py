"""Add offer/address journey models"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1a30851c9eac"
down_revision = "33c2838cfb4a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "address",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("banId", sa.Text(), nullable=True),
        sa.Column("inseeCode", sa.Text(), nullable=False),
        sa.Column("street", sa.Text(), nullable=False),
        sa.Column("postalCode", sa.Text(), nullable=False),
        sa.Column("city", sa.Text(), nullable=False),
        sa.Column("country", sa.Text(), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=8, scale=5), nullable=False),
        sa.Column("longitude", sa.Numeric(precision=8, scale=5), nullable=False),
        sa.CheckConstraint('length("city") <= 50'),
        sa.CheckConstraint('length("inseeCode") = 5'),
        sa.CheckConstraint('length("country") <= 50'),
        sa.CheckConstraint('length("postalCode") = 5'),
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
        "ix_unique_address_per_street_and_insee_code",
        "address",
        ["street", "inseeCode"],
        unique=True,
        postgresql_where=sa.text('"banId" IS NULL'),
    )

    op.create_table(
        "offerer_address",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("addressId", sa.BigInteger(), nullable=True),
        sa.Column("offererId", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["addressId"],
            ["address.id"],
        ),
        sa.ForeignKeyConstraint(
            ["offererId"],
            ["offerer.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_offerer_address_addressId"), "offerer_address", ["addressId"], unique=False)
    op.create_index(op.f("ix_offerer_address_offererId"), "offerer_address", ["offererId"], unique=False)


def downgrade() -> None:
    op.drop_table("offerer_address")
    op.drop_table("address")
