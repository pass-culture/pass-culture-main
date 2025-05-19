"""
add contact request fields to collective offer
"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.educational.models import OfferContactFormEnum
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "df028bd09c15"
down_revision = "7c155945e8fd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("collective_offer_template", sa.Column("contactUrl", sa.Text(), nullable=True))
    op.add_column(
        "collective_offer_template",
        sa.Column(
            "contactForm",
            MagicEnum(OfferContactFormEnum),
            server_default=OfferContactFormEnum.FORM.value,
            default=OfferContactFormEnum.FORM,
            nullable=True,
        ),
    )
    op.execute(
        """
        alter table
            collective_offer_template
        add constraint
            collective_offer_tmpl_contact_request_form_switch_constraint
            check (
                ("contactUrl" is null and "contactForm" is not null)
                or ("contactUrl" is not null and "contactForm" is null)
            ) not valid
    """
    )


def downgrade() -> None:
    op.drop_constraint(
        "collective_offer_tmpl_contact_request_form_switch_constraint", "collective_offer_template", type_="check"
    )

    op.drop_column("collective_offer_template", "contactUrl")
    op.drop_column("collective_offer_template", "contactForm")
