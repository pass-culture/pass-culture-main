"""add roles and backoffice profile link
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "92484e2002ee"
down_revision = "3a90f34b5b14"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "role_backoffice_profile",
        sa.Column("roleId", sa.BigInteger(), nullable=False),
        sa.Column("profileId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["profileId"], ["backoffice_user_profile.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["roleId"], ["role.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("roleId", "profileId"),
    )


def downgrade():
    op.drop_table("role_backoffice_profile")
