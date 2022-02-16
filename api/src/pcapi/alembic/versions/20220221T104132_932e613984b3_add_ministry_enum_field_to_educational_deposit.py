"""add_ministry_enum_field_to_educational_deposit
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "932e613984b3"
down_revision = "d3da2eac435d"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE TYPE ministry AS ENUM ('EDUCATION_NATIONALE', 'MER', 'AGRICULTURE', 'ARMEES')")
    op.add_column(
        "educational_deposit",
        sa.Column(
            "ministry", sa.Enum("EDUCATION_NATIONALE", "MER", "AGRICULTURE", "ARMEES", name="ministry"), nullable=True
        ),
    )


def downgrade():
    op.drop_column("educational_deposit", "ministry")
    op.execute("DROP TYPE ministry")
