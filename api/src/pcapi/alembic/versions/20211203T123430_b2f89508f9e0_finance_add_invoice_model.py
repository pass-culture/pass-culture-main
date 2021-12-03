"""Add Invoice model"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b2f89508f9e0"
down_revision = "f76061a19b8f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "invoice",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("date", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("reference", sa.Text(), nullable=False),
        sa.Column("businessUnitId", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["businessUnitId"],
            ["business_unit.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference"),
    )


def downgrade():
    op.drop_table("invoice")
