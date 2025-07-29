"""Add indexes to the reaction table for offerId and productId."""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e1a6f2f354b8"
down_revision = "0bfe4eb50b49"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_reaction_offerId",
            "reaction",
            ["offerId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            "ix_reaction_productId",
            "reaction",
            ["productId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index("ix_reaction_offerId", table_name="reaction", postgresql_concurrently=True, if_exists=True)
        op.drop_index("ix_reaction_productId", table_name="reaction", postgresql_concurrently=True, if_exists=True)
