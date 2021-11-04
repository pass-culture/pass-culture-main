"""Add Recredit model."""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "49f58959dbd4"
down_revision = "194844a36610"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "recredit",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("depositId", sa.BigInteger(), nullable=False),
        sa.Column("dateCreated", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "recreditType",
            sa.Enum("RECREDIT_16", "RECREDIT_17", name="recredittype", native_enum=False),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["depositId"],
            ["deposit.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("recredit")
