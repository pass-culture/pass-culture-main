"""Set CollectiveOfferRequest.dateCreated non nullable"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "5809622e22d6"
down_revision = "431310254370"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "collective_offer_request",
        "dateCreated",
        existing_type=sa.DATE(),
        nullable=False,
        existing_server_default=sa.text("CURRENT_DATE"),  # type: ignore[arg-type]
    )


def downgrade() -> None:
    op.alter_column(
        "collective_offer_request",
        "dateCreated",
        existing_type=sa.DATE(),
        nullable=True,
        existing_server_default=sa.text("CURRENT_DATE"),  # type: ignore[arg-type]
    )
