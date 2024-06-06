""" Create_offerAddress_table """

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "bf9347d08d33"
down_revision = "2e66d0e6d190"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "offer_address",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=False),
        sa.Column("banId", sa.Text(), nullable=True),
        sa.Column("inseeCode", sa.Text(), nullable=True),
        sa.Column("street", sa.Text(), nullable=True),
        sa.Column("postalCode", sa.Text(), nullable=False),
        sa.Column("city", sa.Text(), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=8, scale=5), nullable=False),
        sa.Column("longitude", sa.Numeric(precision=8, scale=5), nullable=False),
        sa.Column("departmentCode", sa.Text(), nullable=True),
        sa.Column("timezone", sa.Text(), server_default="Europe/Paris", nullable=False),
        sa.CheckConstraint('length("city") <= 50'),
        sa.CheckConstraint('length("departmentCode") = 2 OR length("departmentCode") = 3'),
        sa.CheckConstraint('length("inseeCode") = 5'),
        sa.CheckConstraint('length("postalCode") = 5'),
        sa.CheckConstraint('length("timezone") <= 50'),
        sa.ForeignKeyConstraint(["offerId"], ["offer.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_offer_address_departmentCode"), "offer_address", ["departmentCode"], unique=False, if_not_exists=True
    )
    op.create_index(op.f("ix_offer_address_offerId"), "offer_address", ["offerId"], unique=False, if_not_exists=True)
    op.create_index(
        "ix_partial_unique_address_per_street_and_insee_code_oa",
        "offer_address",
        ["street", "inseeCode"],
        unique=True,
        postgresql_where=sa.text('street IS NOT NULL AND "inseeCode" IS NOT NULL'),
        if_not_exists=True,
    )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_partial_unique_address_per_street_and_insee_code_oa",
            table_name="offer_address",
            if_exists=True,
            postgresql_where=sa.text('street IS NOT NULL AND "inseeCode" IS NOT NULL'),
            postgresql_concurrently=True,
        )
        op.drop_index(
            op.f("ix_offer_address_offerId"), table_name="offer_address", if_exists=True, postgresql_concurrently=True
        )
        op.drop_index(
            op.f("ix_offer_address_departmentCode"),
            table_name="offer_address",
            if_exists=True,
            postgresql_concurrently=True,
        )
    op.drop_table("offer_address")
