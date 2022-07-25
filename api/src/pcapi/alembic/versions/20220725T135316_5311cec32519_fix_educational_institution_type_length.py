"""fix_educational_institution_type_length
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "5311cec32519"
down_revision = "a7accb2d29db"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "educational_institution",
        "institutionType",
        existing_type=sa.String(length=60),
        type_=sa.String(length=80),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "educational_institution",
        "institutionType",
        existing_type=sa.String(length=80),
        type_=sa.String(length=60),
        existing_nullable=False,
    )
