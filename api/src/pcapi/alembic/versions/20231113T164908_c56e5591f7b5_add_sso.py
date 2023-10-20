"""
Add single_sign_on table.
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "c56e5591f7b5"
down_revision = "40dcae913a06"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "single_sign_on",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("ssoProvider", sa.Text(), nullable=False),
        sa.Column("ssoUserId", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ssoProvider", "ssoUserId", name="unique_sso_user_per_sso_provider"),
        sa.UniqueConstraint("ssoProvider", "userId", name="unique_user_per_sso_provider"),
    )
    op.create_index(op.f("ix_single_sign_on_userId"), "single_sign_on", ["userId"], unique=False)


def downgrade() -> None:
    op.drop_table("single_sign_on")
