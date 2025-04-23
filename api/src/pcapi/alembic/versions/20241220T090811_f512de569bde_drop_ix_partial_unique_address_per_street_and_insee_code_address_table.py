"""Drop ix_partial_unique_address_per_street_and_insee_code index on Address table"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f512de569bde"
down_revision = "4c3be4ff5274"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_partial_unique_address_per_street_and_insee_code",
            table_name="address",
            postgresql_where='((street IS NOT NULL) AND ("inseeCode" IS NOT NULL) AND ("isManualEdition" IS NOT TRUE))',
            postgresql_concurrently=True,
            if_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_partial_unique_address_per_street_and_insee_code",
            "address",
            ["street", "inseeCode"],
            unique=True,
            postgresql_where='((street IS NOT NULL) AND ("inseeCode" IS NOT NULL) AND ("isManualEdition" IS NOT TRUE))',
            postgresql_concurrently=True,
            if_not_exists=True,
        )
