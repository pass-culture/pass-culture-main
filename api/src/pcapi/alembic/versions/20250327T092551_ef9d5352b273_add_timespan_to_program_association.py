"""Add a timespan for educational_institution_program_association table.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from pcapi.core.educational.constants import MEG_BEGINNING_DATE


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ef9d5352b273"
down_revision = "38997fdd252c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "educational_institution_program_association",
        sa.Column("timespan", postgresql.TSRANGE(), server_default=f"[{MEG_BEGINNING_DATE},)", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("educational_institution_program_association", "timespan")
