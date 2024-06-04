"""Create index on offer_criterion."criterionId"
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ff36979aea69"
down_revision = "869f869ef1bc"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_offer_criterion_criterionId"),
            "offer_criterion",
            ["criterionId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_offer_criterion_criterionId"),
            table_name="offer_criterion",
            postgresql_concurrently=True,
            if_exists=True,
        )
