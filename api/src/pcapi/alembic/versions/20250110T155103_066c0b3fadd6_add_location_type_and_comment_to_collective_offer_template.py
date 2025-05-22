"""
Add locationType and locationComment to collective_offer_template
"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.educational.models import CollectiveLocationType
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "066c0b3fadd6"
down_revision = "3839712ec2c4"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "collective_offer_template", sa.Column("locationType", MagicEnum(CollectiveLocationType), nullable=True)
    )
    op.add_column("collective_offer_template", sa.Column("locationComment", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("collective_offer_template", "locationComment")
    op.drop_column("collective_offer_template", "locationType")
