"""
Create reaction table
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "e0d7e16bcbaa"
down_revision = "e8732e562de5"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "reaction",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("reactionType", sa.Text(), nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=True),
        sa.Column("productId", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["offerId"],
            ["offer.id"],
            name="reaction_offerId_foreign_key",
            postgresql_not_valid=True,
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["productId"],
            ["product.id"],
            name="reaction_productId_foreign_key",
            postgresql_not_valid=True,
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["userId"], ["user.id"], name="reaction_userId_foreign_key", postgresql_not_valid=True, ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reaction_offerId"), "reaction", ["offerId"], unique=False)
    op.create_index(op.f("ix_reaction_productId"), "reaction", ["productId"], unique=False)
    op.create_index(op.f("ix_reaction_userId"), "reaction", ["userId"], unique=False)
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("reaction_offer_product_user_unique_constraint"),
            "reaction",
            ["userId", "offerId", "productId"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    # squawk has issues with commits like this in the wild. But it also has issue with the following drop_indexes
    # so we need to commit here, squwak is write about the first issue, but not the second
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute("COMMIT")
    op.drop_index(
        op.f("reaction_offer_product_user_unique_constraint"),
        table_name="reaction",
        postgresql_concurrently=True,
        if_exists=True,
    )
    op.drop_index(op.f("ix_reaction_userId"), table_name="reaction", postgresql_concurrently=True, if_exists=True)
    op.drop_index(op.f("ix_reaction_productId"), table_name="reaction", postgresql_concurrently=True, if_exists=True)
    op.drop_index(op.f("ix_reaction_offerId"), table_name="reaction", postgresql_concurrently=True, if_exists=True)
    op.drop_table("reaction")
