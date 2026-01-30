"""Create indexes on table: non_payment_notice_batch_association"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8f6a72170afd"
down_revision = "237ce7304502"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_non_payment_notice_batch_association_batchId"),
            "non_payment_notice_batch_association",
            ["batchId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            op.f("ix_non_payment_notice_batch_association_noticeId"),
            "non_payment_notice_batch_association",
            ["noticeId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_non_payment_notice_batch_association_noticeId"),
            table_name="non_payment_notice_batch_association",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f("ix_non_payment_notice_batch_association_batchId"),
            table_name="non_payment_notice_batch_association",
            postgresql_concurrently=True,
            if_exists=True,
        )
