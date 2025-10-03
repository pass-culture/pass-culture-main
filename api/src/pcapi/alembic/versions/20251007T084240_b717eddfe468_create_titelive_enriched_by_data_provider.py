"""Create Titelive Enriched by Data provider"""

from alembic import op

from pcapi.core.providers import constants as providers_constants


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b717eddfe468"
down_revision = "be57eb4e814a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        f"""
        INSERT INTO provider (name, "localClass", "enabledForPro", "isActive")
        VALUES ('{providers_constants.TITELIVE_ENRICHED_BY_DATA}', null, false, true)
        """
    )


def downgrade() -> None:
    op.execute(
        f"""
        DELETE FROM provider WHERE name = '{providers_constants.TITELIVE_ENRICHED_BY_DATA}'
        """
    )
