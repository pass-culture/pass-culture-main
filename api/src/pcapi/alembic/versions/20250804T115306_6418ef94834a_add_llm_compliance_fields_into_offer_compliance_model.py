"""Add llm_compliance fields_into OfferCompliance_model"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.offers.models import LLMComplianceValidationStatus
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "6418ef94834a"
down_revision = "82773754a29f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "offer_compliance", sa.Column("llm_validation_status", MagicEnum(LLMComplianceValidationStatus), nullable=True)
    )
    op.add_column("offer_compliance", sa.Column("llm_explanation", sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column("offer_compliance", "llm_validation_status")
    op.drop_column("offer_compliance", "llm_explanation")
