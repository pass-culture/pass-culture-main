"""rename_booking_column

Revision ID: 19b36a0b880a
Revises: 0211bd1e44e2
Create Date: 2021-07-20 15:40:11.661123

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "19b36a0b880a"
down_revision = "0211bd1e44e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
    ALTER TABLE public.booking
    RENAME COLUMN "confirmationDate"
    TO "cancellationLimitDate";
    """
    )


def downgrade() -> None:
    op.execute(
        """
    ALTER TABLE public.booking
    RENAME COLUMN "cancellationLimitDate"
    TO "confirmationDate";
    """
    )
