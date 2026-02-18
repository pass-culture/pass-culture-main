"""Drop OfferReport"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "38afc60a955c"
down_revision = "055f840f1976"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_table("offer_report")


def downgrade() -> None:
    op.create_table(
        "offer_report",
        sa.Column("id", sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("offerId", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column(
            "reportedAt", postgresql.TIMESTAMP(), server_default=sa.text("now()"), autoincrement=False, nullable=False
        ),
        sa.Column("reason", sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column("customReasonContent", sa.TEXT(), autoincrement=False, nullable=True),
        sa.CheckConstraint(
            "reason <> 'OTHER'::text AND \"customReasonContent\" IS NULL OR reason = 'OTHER'::text AND \"customReasonContent\" IS NOT NULL AND btrim(\"customReasonContent\", ' '::text) <> ''::text",
            name=op.f("custom_reason_null_only_if_reason_is_other"),
        ),
        sa.ForeignKeyConstraint(["offerId"], ["offer.id"], name=op.f("offer_report_offerId_fkey")),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], name=op.f("offer_report_userId_fkey")),
        sa.PrimaryKeyConstraint("id", name=op.f("offer_report_pkey")),
        sa.UniqueConstraint(
            "userId",
            "offerId",
            name=op.f("unique_offer_per_user"),
            postgresql_include=[],
            postgresql_nulls_not_distinct=False,
        ),
    )
