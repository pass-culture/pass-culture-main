"""index column venueId for table pro_advice"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "cb2f79ae8fc2"
down_revision = "9252f2f14ae9"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_pro_advice_venueId"),
            "pro_advice",
            ["venueId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(op.f("ix_pro_advice_venueId"), "pro_advice", postgresql_concurrently=True, if_exists=True)
