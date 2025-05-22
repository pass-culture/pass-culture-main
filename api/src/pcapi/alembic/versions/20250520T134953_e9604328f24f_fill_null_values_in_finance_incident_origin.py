"""
Fill null values in finance_incident.origin

The 'Add NOT NULL constraint on "finance_incident.origin"' was making the origin column non-nullable, after having filled the empty values with a separate script.

This migration will break in case the script has not been run first, thus this step added here
"""

from alembic import op

from pcapi.core.finance.models import FinanceIncidentRequestOrigin


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e9604328f24f"
down_revision = "3f7aeffafcab"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    query = f"""
        UPDATE finance_incident
        SET origin = '{FinanceIncidentRequestOrigin.SUPPORT_PRO.value}'
        WHERE finance_incident.origin IS NULL;
        """
    op.execute(query)


def downgrade() -> None:
    pass
