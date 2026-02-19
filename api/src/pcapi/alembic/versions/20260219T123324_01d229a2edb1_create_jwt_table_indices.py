"""create user table indices"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "01d229a2edb1"
down_revision = "2b3c6f475197"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_native_user_session_deviceId"),
            "native_user_session",
            ["deviceId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            op.f("ix_native_user_session_expirationDatetime"),
            "native_user_session",
            ["expirationDatetime"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            op.f("ix_native_user_session_userId"),
            "native_user_session",
            ["userId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_native_user_session_userId"),
            table_name="native_user_session",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f("ix_native_user_session_expirationDatetime"),
            table_name="native_user_session",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f("ix_native_user_session_deviceId"),
            table_name="native_user_session",
            postgresql_concurrently=True,
            if_exists=True,
        )
