"""Add `customReimbursementRuleId` in `payment` table

Revision ID: b74c334c8095
Revises: d93ff67e391f
Create Date: 2021-06-07 18:10:15.871587

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b74c334c8095"
down_revision = "d93ff67e391f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("payment", sa.Column("customReimbursementRuleId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(None, "payment", "custom_reimbursement_rule", ["customReimbursementRuleId"], ["id"])


def downgrade():
    op.drop_column("payment", "customReimbursementRuleId")
