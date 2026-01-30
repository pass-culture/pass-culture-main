"""Migrate existing data to non_payment_notice_batch_association"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "54de74fd92f8"
down_revision = "8f6a72170afd"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        sa.text("""
                INSERT INTO non_payment_notice_batch_association ("noticeId", "batchId")
                SELECT id, "batchId"
                FROM non_payment_notice
                WHERE "batchId" IS NOT NULL
                ON CONFLICT DO NOTHING;
                """)
    )


def downgrade() -> None:
    pass
