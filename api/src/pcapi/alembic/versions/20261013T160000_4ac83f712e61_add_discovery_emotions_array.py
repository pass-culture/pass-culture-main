"""Add the discovery emotions array alongside the existing scalar column."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
revision = "4ac83f712e61"
down_revision = "62b8943e7ac1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("discovery", sa.Column("emotions", postgresql.ARRAY(sa.Text()), nullable=True))
    op.create_check_constraint(
        "check_discovery_emotions",
        "discovery",
        "emotions IS NULL OR (array_position(emotions, NULL) IS NULL AND emotions <@ "
        "ARRAY['intrigu\u00e9', '\u00e9merveill\u00e9', 'touch\u00e9', 'surpris', 'bouscul\u00e9', "
        "'indiff\u00e9rent']::text[])",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("check_discovery_emotions", "discovery", type_="check")
    op.drop_column("discovery", "emotions")
