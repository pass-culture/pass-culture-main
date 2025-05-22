"""Add "AllocineProducts" in table "provider" """

from alembic import op

from pcapi.core.providers import constants as providers_constants


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "7894be402ca7"
down_revision = "fc7dd42a29ac"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        f"""
        INSERT INTO provider (name, "localClass", "apiUrl", "enabledForPro", "isActive")
        VALUES ('{providers_constants.ALLOCINE_PRODUCTS_PROVIDER_NAME}', null, null, false, true)
        """
    )


def downgrade() -> None:
    pass
