"""Add pricing-related models."""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1f2f37dfc23d"
down_revision = "32c7ca9be253"
branch_labels = None
depends_on = None


def upgrade():
    import pcapi.core.finance.models as finance_models
    import pcapi.utils.db as db_utils

    op.create_table(
        "pricing",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("status", db_utils.MagicEnum(finance_models.PricingStatus), nullable=False),
        sa.Column("bookingId", sa.BigInteger(), nullable=False),
        sa.Column("businessUnitId", sa.BigInteger(), nullable=False),
        sa.Column("creationDate", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("valueDate", sa.DateTime(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("standardRule", sa.Text(), nullable=False),
        sa.Column("customRuleId", sa.BigInteger(), nullable=True),
        sa.Column("revenue", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["bookingId"],
            ["booking.id"],
        ),
        sa.ForeignKeyConstraint(
            ["businessUnitId"],
            ["business_unit.id"],
        ),
        sa.ForeignKeyConstraint(
            ["customRuleId"],
            ["custom_reimbursement_rule.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_uniq_booking_id",
        "pricing",
        ["bookingId"],
        unique=True,
        postgresql_where=sa.text("status != 'cancelled'"),
    )
    op.create_index(op.f("ix_pricing_bookingId"), "pricing", ["bookingId"], unique=False)
    op.create_index(op.f("ix_pricing_businessUnitId"), "pricing", ["businessUnitId"], unique=False)
    op.create_index(op.f("ix_pricing_customRuleId"), "pricing", ["customRuleId"], unique=False)
    op.create_index(op.f("ix_pricing_status"), "pricing", ["status"], unique=False)
    op.execute(
        """
ALTER TABLE pricing
ADD CONSTRAINT reimbursement_rule_constraint_check
CHECK (
    (
        "standardRule" = ''
        AND "customRuleId" IS NOT NULL
    ) OR (
        "standardRule" != ''
        AND "customRuleId" IS NULL
    )
)"""
    )

    op.create_table(
        "pricing_line",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("pricingId", sa.BigInteger(), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("category", db_utils.MagicEnum(finance_models.PricingLineCategory), nullable=False),
        sa.ForeignKeyConstraint(
            ["pricingId"],
            ["pricing.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "pricing_log",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("pricingId", sa.BigInteger(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("statusBefore", db_utils.MagicEnum(finance_models.PricingStatus), nullable=False),
        sa.Column("statusAfter", db_utils.MagicEnum(finance_models.PricingStatus), nullable=False),
        sa.Column("reason", db_utils.MagicEnum(finance_models.PricingLogReason), nullable=False),
        sa.ForeignKeyConstraint(
            ["pricingId"],
            ["pricing.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pricing_log_pricingId"), "pricing_log", ["pricingId"], unique=False)


def downgrade():
    op.drop_table("pricing_log")
    op.drop_table("pricing_line")
    op.drop_table("pricing")
