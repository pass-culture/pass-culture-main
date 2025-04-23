"""Drop deprecated index: idx_venue_trgm_public_name"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0e5b68c5865d"
down_revision = "833b6aed7272"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "idx_venue_trgm_public_name",
            table_name="venue",
            postgresql_using="gin",
            postgresql_concurrently=True,
            if_exists=True,
        )


def downgrade() -> None:
    # Index was no longer used since unaccented index has been created, we will never rollback 6 iterations in the past
    pass
