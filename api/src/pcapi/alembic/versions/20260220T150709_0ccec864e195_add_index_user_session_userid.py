"""add index user_session.userId"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0ccec864e195"
down_revision = "7a48fa667aa3"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_user_session_userId"),
            "user_session",
            ["userId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_user_session_userId"),
            table_name="user_session",
            postgresql_concurrently=True,
            if_exists=True,
        )
