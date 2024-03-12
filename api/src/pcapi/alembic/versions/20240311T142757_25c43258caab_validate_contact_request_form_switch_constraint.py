"""Validate contact_request_form_switch constraint
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "25c43258caab"
down_revision = "4df45e259f14"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(
            'ALTER TABLE "collective_offer_template" VALIDATE CONSTRAINT "collective_offer_tmpl_contact_request_form_switch_constraint"'
        )


def downgrade() -> None:
    pass
