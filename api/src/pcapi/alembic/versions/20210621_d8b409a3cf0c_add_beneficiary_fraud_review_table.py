"""add beneficiary_fraud_review table

Revision ID: d8b409a3cf0c
Revises: bb6bf7b9cdbd
Create Date: 2021-06-21 16:05:16.973267

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d8b409a3cf0c"
down_revision = "bb6bf7b9cdbd"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "beneficiary_fraud_review",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("authorId", sa.BigInteger(), nullable=False),
        sa.Column("review", sa.Text(), nullable=True),
        sa.Column("dateReviewed", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["authorId"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["userId"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_beneficiary_fraud_review_authorId"), "beneficiary_fraud_review", ["authorId"], unique=False
    )
    op.create_index(op.f("ix_beneficiary_fraud_review_userId"), "beneficiary_fraud_review", ["userId"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_beneficiary_fraud_review_userId"), table_name="beneficiary_fraud_review")
    op.drop_index(op.f("ix_beneficiary_fraud_review_authorId"), table_name="beneficiary_fraud_review")
    op.drop_table("beneficiary_fraud_review")
