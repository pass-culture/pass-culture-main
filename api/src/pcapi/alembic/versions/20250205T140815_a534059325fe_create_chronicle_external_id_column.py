"""create column chronicle.externalId"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a534059325fe"
down_revision = "8ee08df65b28"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("chronicle", sa.Column("externalId", sa.Text()))


def downgrade() -> None:
    op.drop_column("chronicle", "externalId")
