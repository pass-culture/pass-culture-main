"""Delete ununsed Individual offer Api provider (revert 2e171418aa71)
"""
from alembic import op

from pcapi import settings
import pcapi.core.providers.constants as providers_constants


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "33e76b6e3a77"
down_revision = "4ed5060d7fd7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Some offer have this provider in integration, don't touch it
    if settings.IS_INTEGRATION:
        return
    op.execute(
        f"""DELETE FROM provider WHERE "localClass" = '{providers_constants.INDIVIDUAL_OFFERS_API_FAKE_CLASS_NAME}'"""
    )


def downgrade() -> None:
    # Some offer have this provider in integration, don't touch it
    if settings.IS_INTEGRATION:
        return
    op.execute(
        f"""
        INSERT INTO provider (name, "localClass", "apiUrl", "enabledForPro", "isActive")
        VALUES ('{providers_constants.INDIVIDUAL_OFFERS_API_PROVIDER_NAME}', '{providers_constants.INDIVIDUAL_OFFERS_API_FAKE_CLASS_NAME}', null, false, true)
        """
    )
