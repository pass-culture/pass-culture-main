"""Make CinemaProviderPivot venueId column non nullable"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0403f97207ba"
down_revision = "166608debd4c"
branch_labels: tuple | None = None
depends_on: tuple | None = None


def upgrade() -> None:
    op.alter_column("cinema_provider_pivot", "venueId", existing_type=sa.BIGINT(), nullable=False)


def downgrade() -> None:
    op.alter_column("cinema_provider_pivot", "venueId", existing_type=sa.BIGINT(), nullable=True)
