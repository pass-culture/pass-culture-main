"""add_individual_offer_api_provider_api
"""
from alembic import op

from pcapi.core.providers import constants as providers_constants


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "2e171418aa71"
down_revision = "7b3320f4bd9a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        f"""
        INSERT INTO provider (name, "localClass", "apiUrl", "enabledForPro", "isActive")
        VALUES ('{providers_constants.INDIVIDUAL_OFFERS_API_PROVIDER_NAME}', '{providers_constants.INDIVIDUAL_OFFERS_API_FAKE_CLASS_NAME}', null, false, true)
        """
    )


def downgrade() -> None:
    op.execute(
        f"""DELETE FROM provider WHERE "localClass" = '{providers_constants.INDIVIDUAL_OFFERS_API_FAKE_CLASS_NAME}'"""
    )
