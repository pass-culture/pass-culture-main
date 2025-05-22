"""update collective offer template's contact's constraints"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "fa4755bb92f0"
down_revision = "8d4e8ebb573c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("collective_offer_template", "contactEmail", existing_type=sa.VARCHAR(length=120), nullable=True)
    op.execute(
        """
        ALTER TABLE
            collective_offer_template
        DROP CONSTRAINT
            collective_offer_tmpl_contact_request_form_switch_constraint
        """
    )
    op.execute(
        """
        ALTER TABLE
            collective_offer_template
        ADD CONSTRAINT
            collective_offer_tmpl_contact_request_form_switch_constraint
            check (
                ("contactUrl" IS NULL OR "contactForm" IS NULL)
            ) not valid
    """
    )


def downgrade() -> None:
    op.alter_column("collective_offer_template", "contactEmail", existing_type=sa.VARCHAR(length=120), nullable=False)
