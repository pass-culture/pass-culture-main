"""Add column: backoffice_profile.dsInstructorId"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "3b79fd434823"
down_revision = "ca78c57a4f44"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("backoffice_user_profile", sa.Column("dsInstructorId", sa.Text(), nullable=True))
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_backoffice_user_profile_dsInstructorId"),
            "backoffice_user_profile",
            ["dsInstructorId"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_backoffice_user_profile_dsInstructorId"),
            table_name="backoffice_user_profile",
            postgresql_concurrently=True,
            if_exists=True,
        )
    op.drop_column("backoffice_user_profile", "dsInstructorId")
