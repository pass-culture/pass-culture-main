"""Create unique index on settlement_batch.externalId"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3b3ffca589b5"
down_revision = "4ca6a8b4c003"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_settlement_batch_externalId"),
            "settlement_batch",
            ["externalId"],
            unique=True,
            if_not_exists=True,
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_settlement_batch_externalId"),
            table_name="settlement_batch",
            if_exists=True,
            postgresql_concurrently=True,
        )
