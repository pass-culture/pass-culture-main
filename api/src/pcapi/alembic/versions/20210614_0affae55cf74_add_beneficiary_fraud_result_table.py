"""add beneficiary_fraud_result table

Revision ID: 0affae55cf74
Revises: 212db74b847d
Create Date: 2021-06-14 16:33:06.831041

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0affae55cf74"
down_revision = "212db74b847d"
branch_labels = None
depends_on = None


def upgrade():
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
    )
    op.create_index(op.f("ix_beneficiary_fraud_result_userId"), "beneficiary_fraud_result", ["userId"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_beneficiary_fraud_result_userId"), table_name="beneficiary_fraud_result")
    op.drop_table("beneficiary_fraud_result")
