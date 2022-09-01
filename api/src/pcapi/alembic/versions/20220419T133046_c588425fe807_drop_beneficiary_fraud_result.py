"""drop_beneficiary_fraud_result
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "c588425fe807"
down_revision = "b63eb1053857"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("beneficiary_fraud_result")


def downgrade() -> None:
    op.create_table(
        "beneficiary_fraud_result",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.Text(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("dateCreated", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("dateUpdated", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["userId"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.Column(
            "reason_codes",
            postgresql.ARRAY(sa.TEXT()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("eligibilityType", sa.TEXT(), server_default=None, nullable=True),
    )
