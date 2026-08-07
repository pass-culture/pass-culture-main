"""
Add collective_offer_template check constraint on contact fields
and reaction constraint on productId and offerId
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2f3fe3269031"
down_revision = "b3e1f2a4c5d6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "collective_offer_tmpl_contact_request_form_data_constraint",
        table_name="collective_offer_template",
        condition=sa.text(
            '("contactEmail" is not null) or ("contactPhone" is not null) or ("contactUrl" is not null) or ("contactForm" is not null)'
        ),
        postgresql_not_valid=True,
    )

    op.create_check_constraint(
        "reaction_offer_product_check",
        table_name="reaction",
        condition=sa.text(
            '("offerId" is not null and "productId" is null) or ("productId" is not null and "offerId" is null)'
        ),
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint(
        "reaction_offer_product_check",
        table_name="reaction",
    )

    op.drop_constraint(
        "collective_offer_tmpl_contact_request_form_data_constraint",
        table_name="collective_offer_template",
    )
