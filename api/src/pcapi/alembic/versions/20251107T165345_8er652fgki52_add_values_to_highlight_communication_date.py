"""Add values to highlight.communication_date"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8er652fgki52"
down_revision = "9204a54813bb"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE highlight
            SET communication_date = lower(highlight_datespan)::date
            """
        )
    )


def downgrade() -> None:
    pass
