"""Drop subcategoryId in CollectiveOfferTemplate"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d01d0e1ad810"
down_revision = "b686ce67191b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("collective_offer_template", "subcategoryId")


def downgrade() -> None:
    op.add_column(
        "collective_offer_template", sa.Column("subcategoryId", sa.TEXT(), autoincrement=False, nullable=True)
    )
