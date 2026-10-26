"""Add column banner_id to be used instead of banner_url"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "f32f7be3fc7f"
down_revision = "e4a6d665249c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("google_places_info", sa.Column("bannerId", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("google_places_info", "bannerId")
