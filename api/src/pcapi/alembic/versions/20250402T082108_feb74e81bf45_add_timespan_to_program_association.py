"""Add a timespan for educational_institution_program_association table.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "feb74e81bf45"
down_revision = "38997fdd252c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "educational_institution_program_association",
        sa.Column(
            "timespan",
            postgresql.TSRANGE(),
            nullable=False,
            server_default=sa.text("'[\"2023-09-01 00:00:00\",)'::tsrange"),
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "educational_institution_program_association",
        "timespan",
    )
