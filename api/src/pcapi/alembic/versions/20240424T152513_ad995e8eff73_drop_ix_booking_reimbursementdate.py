"""Drop ix_booking_reimbursementDate index"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ad995e8eff73"
down_revision = "c51c13995e1f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_booking_reimbursementDate",
            table_name="booking",
            postgresql_using="gin",
            postgresql_concurrently=True,
            if_exists=True,
        )


def downgrade() -> None:
    pass
