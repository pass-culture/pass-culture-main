"""validate collective offer template contact form constraint"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1e3979b7adb0"
down_revision = "00738a9d13b0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        alter table
            collective_offer_template
        validate constraint
            collective_offer_tmpl_contact_request_form_switch_constraint
    """
    )


def downgrade() -> None:
    pass
