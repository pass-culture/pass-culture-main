"""Remove indexes "ix_reaction_offerId" and "ix_reaction_productId" in table "reaction" """

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "280eae6d44f0"
down_revision = "9954d7d01119"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade():
    with op.get_context().autocommit_block():
        op.drop_index("ix_reaction_offerId", table_name="reaction", postgresql_concurrently=True, if_exists=True)
        op.drop_index("ix_reaction_productId", table_name="reaction", postgresql_concurrently=True, if_exists=True)


def downgrade():
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
