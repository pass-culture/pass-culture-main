"""
eac collective offer teamplte contactform default form null
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1ac22a2f313e"
down_revision = "ccd86b897e7a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "collective_offer_template", "contactForm", existing_type=sa.TEXT(), server_default=None, existing_nullable=True
    )


def downgrade() -> None:
    op.alter_column(
        "collective_offer_template",
        "contactForm",
        existing_type=sa.TEXT(),
        server_default=sa.text("'form'::text"),
        existing_nullable=True,
    )
