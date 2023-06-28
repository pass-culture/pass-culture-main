"""Add user id to offerer invitation table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "117312f339eb"
down_revision = "6d60c6c70ac3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("offerer_invitation", sa.Column("userId", sa.BigInteger(), nullable=False))
    op.create_index(op.f("ix_offerer_invitation_userId"), "offerer_invitation", ["userId"], unique=False)
    op.create_foreign_key("offerer_invitation_userId_fkey", "offerer_invitation", "user", ["userId"], ["id"])


def downgrade() -> None:
    op.drop_constraint("offerer_invitation_userId_fkey", "offerer_invitation", type_="foreignkey")
    op.drop_index(op.f("ix_offerer_invitation_userId"), table_name="offerer_invitation")
    op.drop_column("offerer_invitation", "userId")
