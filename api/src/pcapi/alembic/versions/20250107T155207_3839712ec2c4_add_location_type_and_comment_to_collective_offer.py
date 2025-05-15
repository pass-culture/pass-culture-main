"""
Add locationType and locationComment to collective_offer
"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.educational.models import CollectiveLocationType
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "3839712ec2c4"
down_revision = "ab6fe51d82bb"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("collective_offer", sa.Column("locationType", MagicEnum(CollectiveLocationType), nullable=True))
    op.add_column("collective_offer", sa.Column("locationComment", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("collective_offer", "locationComment")
    op.drop_column("collective_offer", "locationType")
