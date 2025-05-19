"""Drop "Token" table"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ce97cf13d894"
down_revision = "04caadcaa652"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("token")


def downgrade() -> None:
    op.create_table(
        "token",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("type", sa.Enum("RESET_PASSWORD", name="tokentype"), nullable=False),
        sa.Column("creationDate", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("expirationDate", sa.DateTime(), nullable=True),
        sa.Column("isUsed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("extraData", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_token_userId"), "token", ["userId"], unique=False)
    op.create_index(op.f("ix_token_value"), "token", ["value"], unique=True)
