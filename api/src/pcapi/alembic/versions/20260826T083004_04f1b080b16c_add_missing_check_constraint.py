"""Add missing check constraint on collective offer template"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "04f1b080b16c"
down_revision = "122d35fd4ffe"
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


def downgrade() -> None:
    op.drop_constraint(
        "collective_offer_tmpl_contact_request_form_data_constraint",
        table_name="collective_offer_template",
    )
