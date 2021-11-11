"""Various changes on CustomReimbursementRule model."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.dialects import postgresql

from pcapi.core.payments.models import CustomReimbursementRule


# revision identifiers, used by Alembic.
revision = "4317a4dc233e"
down_revision = "31422b3fe853"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("custom_reimbursement_rule", sa.Column("rate", sa.NUMERIC(precision=3, scale=2), nullable=True))
    op.alter_column(
        "custom_reimbursement_rule", "amount", existing_type=sa.NUMERIC(precision=10, scale=2), nullable=True
    )
    op.add_column(
        "custom_reimbursement_rule",
        sa.Column("categories", postgresql.ARRAY(sa.Text()), server_default="{}", nullable=True),
    )
    op.add_column("custom_reimbursement_rule", sa.Column("offererId", sa.BigInteger(), nullable=True))
    op.alter_column("custom_reimbursement_rule", "offerId", existing_type=sa.BIGINT(), nullable=True)
    op.create_foreign_key(None, "custom_reimbursement_rule", "offerer", ["offererId"], ["id"])
    op.create_check_constraint(
        "offer_or_offerer_check",
        "custom_reimbursement_rule",
        func.num_nonnulls(CustomReimbursementRule.offerId, CustomReimbursementRule.offererId) == 1,
    )
    op.create_check_constraint(
        "amount_or_rate_check",
        "custom_reimbursement_rule",
        func.num_nonnulls(CustomReimbursementRule.amount, CustomReimbursementRule.rate) == 1,
    )
    op.execute(
        """ALTER TABLE custom_reimbursement_rule """
        """ADD CONSTRAINT rate_range_check """
        """CHECK (rate IS NULL OR (rate BETWEEN 0 AND 1))"""
    )


def downgrade():
    op.drop_column("custom_reimbursement_rule", "rate")
    op.drop_constraint("amount_or_rate_check", "custom_reimbursement_rule")
    op.drop_constraint("offer_or_offerer_check", "custom_reimbursement_rule")
    # Restore NOT NULL constraint on `offerId`
    op.alter_column("custom_reimbursement_rule", "offerId", existing_type=sa.BIGINT(), nullable=False)
    op.drop_column("custom_reimbursement_rule", "offererId")
    op.drop_column("custom_reimbursement_rule", "categories")
