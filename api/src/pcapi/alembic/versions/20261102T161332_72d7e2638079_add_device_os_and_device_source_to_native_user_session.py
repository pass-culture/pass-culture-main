"""Add deviceOs and deviceSource cols to native_user_session table."""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "72d7e2638079"
down_revision = "9780c43c7c0c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "native_user_session",
        sa.Column(
            "deviceOs",
            sa.Text(),
            nullable=True,
        ),
        if_not_exists=True,
    )
    op.add_column(
        "native_user_session",
        sa.Column(
            "deviceSource",
            sa.Text(),
            nullable=True,
        ),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_column("native_user_session", "deviceSource")
    op.drop_column("native_user_session", "deviceOs")
