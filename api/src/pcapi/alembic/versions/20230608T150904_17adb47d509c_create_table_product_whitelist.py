"""Create "product_whitelist" table
"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "17adb47d509c"
down_revision = "54974ef1d55a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_whitelist",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("ean", sa.String(length=13), nullable=False, unique=True, index=True),
        sa.Column(
            "dateCreated",
            sa.DateTime(),
            default=datetime.utcnow,
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("authorId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["authorId"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("product_whitelist")
