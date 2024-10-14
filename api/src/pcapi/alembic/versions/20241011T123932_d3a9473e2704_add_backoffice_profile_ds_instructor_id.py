"""Add column: backoffice_profile.dsInstructorId
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d3a9473e2704"
down_revision = "b409480c6113"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("backoffice_user_profile", sa.Column("dsInstructorId", sa.Text(), nullable=True))
    op.create_unique_constraint(
        "backoffice_user_profile_unique_dsInstructorId", "backoffice_user_profile", ["dsInstructorId"]
    )


def downgrade() -> None:
    op.drop_constraint("backoffice_user_profile_unique_dsInstructorId", "backoffice_user_profile", type_="unique")
    op.drop_column("backoffice_user_profile", "dsInstructorId")
