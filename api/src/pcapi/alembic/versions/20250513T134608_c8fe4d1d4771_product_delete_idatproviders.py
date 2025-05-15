"""Delete idAtProviders column from product table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c8fe4d1d4771"
down_revision = "1eb6460032d1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("product", "idAtProviders")


def downgrade() -> None:
    # We wouldn't want to create a unique constraint during a downgrade
    # If we ever wanted to revert this migration, we should do some custom migrations to add the constraint again
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.add_column("product", sa.Column("idAtProviders", sa.VARCHAR(length=70), autoincrement=False, nullable=True))
