"""Drop deprecated index: idx_offerer_trgm_name"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "348fd34d687b"
down_revision = "0e5b68c5865d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "idx_offerer_trgm_name",
            table_name="offerer",
            postgresql_using="gin",
            postgresql_concurrently=True,
            if_exists=True,
        )


def downgrade() -> None:
    # Index was no longer used since unaccented index has been created, we will never rollback 6 iterations in the past
    pass
