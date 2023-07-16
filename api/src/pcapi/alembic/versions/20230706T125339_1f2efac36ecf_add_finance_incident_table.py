"""
Add `finance_incident` table
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1f2efac36ecf"
down_revision = "08dfd555fca2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "finance_incident",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column(
            "kind",
            sa.Enum(
                "OVERPAYMENT",
                "COMMERCIAL_GESTURE",
                "OFFER_PRICE_REGULATION",
                "FRAUD",
                name="incidenttype",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("CREATED", "VALIDATED", "CANCELLED", name="incidentstatus", native_enum=False),
            server_default="created",
            nullable=False,
        ),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("finance_incident")
