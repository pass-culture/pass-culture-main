"""
add preferences (jsonb) to educational redactor
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "c1c137b863fe"
down_revision = "97fcc93be70a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "educational_redactor",
        sa.Column("preferences", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("educational_redactor", "preferences")
