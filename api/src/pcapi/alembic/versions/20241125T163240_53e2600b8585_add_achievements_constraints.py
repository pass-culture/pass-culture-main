"""Add achievements FK constraints"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "53e2600b8585"
down_revision = "1007ef88d004"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "achievement_userId_fkey",
        "achievement",
        "user",
        ["userId"],
        ["id"],
        postgresql_not_valid=True,
    )
    op.create_foreign_key(
        "achievement_bookingId_fkey",
        "achievement",
        "booking",
        ["bookingId"],
        ["id"],
        postgresql_not_valid=True,
    )
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_achievement_userId"),
            "achievement",
            ["userId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_achievement_userId"),
            table_name="achievement",
            postgresql_concurrently=True,
            if_exists=True,
        )
