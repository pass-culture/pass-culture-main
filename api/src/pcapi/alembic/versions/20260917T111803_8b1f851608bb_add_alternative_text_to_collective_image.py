"""Add alternative text to collective image
To be compliant with accessibility standards
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "8b1f851608bb"
down_revision = "50df4d24f087"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("collective_offer", sa.Column("imageAlternativeText", sa.Text(), nullable=True))
    op.add_column("collective_offer_template", sa.Column("imageAlternativeText", sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_column("collective_offer_template", "imageAlternativeText")
    op.drop_column("collective_offer", "imageAlternativeText")
