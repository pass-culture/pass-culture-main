"""Update index on address: ix_partial_unique_address_per_street_and_insee_code
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "036a69733891"
down_revision = "61a200a27055"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_partial_unique_address_per_street_and_insee_code",
            table_name="address",
            postgresql_where=sa.text('((street IS NOT NULL) AND ("inseeCode" IS NOT NULL))'),
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.create_index(
            "ix_partial_unique_address_per_street_and_insee_code",
            "address",
            ["street", "inseeCode"],
            unique=True,
            postgresql_where=sa.text(
                'street IS NOT NULL AND "inseeCode" IS NOT NULL AND "isManualEdition" IS NOT true'
            ),
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_partial_unique_address_per_street_and_insee_code",
            table_name="address",
            postgresql_where=sa.text(
                'street IS NOT NULL AND "inseeCode" IS NOT NULL AND "isManualEdition" IS NOT true'
            ),
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.create_index(
            "ix_partial_unique_address_per_street_and_insee_code",
            "address",
            ["street", "inseeCode"],
            unique=True,
            postgresql_where=sa.text('((street IS NOT NULL) AND ("inseeCode" IS NOT NULL))'),
            postgresql_concurrently=True,
            if_not_exists=True,
        )
