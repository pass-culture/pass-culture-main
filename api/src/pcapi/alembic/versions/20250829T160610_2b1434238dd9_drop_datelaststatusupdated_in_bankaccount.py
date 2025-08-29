"""Drop dateLastStatusUpdate in BankAccount"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2b1434238dd9"
down_revision = "cd92fbabf123"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("bank_account", "dateLastStatusUpdate")


def downgrade() -> None:
    op.add_column(
        "bank_account", sa.Column("dateLastStatusUpdate", postgresql.TIMESTAMP(), autoincrement=False, nullable=True)
    )
