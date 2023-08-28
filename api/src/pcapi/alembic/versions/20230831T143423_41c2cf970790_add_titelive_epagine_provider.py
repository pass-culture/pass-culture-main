""" Add TiteLive Epagine provider
"""
from alembic import op

from pcapi.core.providers import constants as providers_constants


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "41c2cf970790"
down_revision = "c8c904df59fd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        f"""
        INSERT INTO provider (name, "localClass", "apiUrl", "enabledForPro", "isActive")
        VALUES ('{providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME}', null, null, false, true)
        """
    )


def downgrade() -> None:
    op.execute(f"""DELETE FROM provider WHERE "name" = '{providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME}'""")
