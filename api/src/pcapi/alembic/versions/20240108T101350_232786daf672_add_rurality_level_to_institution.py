"""add rurality_level to EductionInstitution"""

from alembic import op
import sqlalchemy as sa

from pcapi.core.educational.models import InstitutionRuralLevel
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "232786daf672"
down_revision = "945ba5efc72f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("educational_institution", sa.Column("ruralLevel", MagicEnum(InstitutionRuralLevel), nullable=True))


def downgrade() -> None:
    op.drop_column("educational_institution", "ruralLevel")
