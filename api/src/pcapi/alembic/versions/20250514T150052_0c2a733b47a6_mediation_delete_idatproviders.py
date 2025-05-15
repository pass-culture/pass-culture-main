"""Delete idAtProviders column from mediation table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0c2a733b47a6"
down_revision = "4de5a07c2f6e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("mediation", "idAtProviders")


def downgrade() -> None:
    # We wouldn't want to create a unique constraint during a downgrade
    # If we ever wanted to revert this migration, we should do some custom migrations to add the constraint again
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.add_column("mediation", sa.Column("idAtProviders", sa.VARCHAR(length=70), autoincrement=False, nullable=True))
