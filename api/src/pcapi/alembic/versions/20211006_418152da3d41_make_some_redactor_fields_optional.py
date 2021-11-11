"""make_some_redactor_fields_optional
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "418152da3d41"
down_revision = "5129a4e3aabb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("educational_redactor", "civility", existing_type=sa.VARCHAR(length=20), nullable=True)
    op.alter_column("educational_redactor", "firstName", existing_type=sa.VARCHAR(length=128), nullable=True)
    op.alter_column("educational_redactor", "lastName", existing_type=sa.VARCHAR(length=128), nullable=True)


def downgrade() -> None:
    op.alter_column("educational_redactor", "lastName", existing_type=sa.VARCHAR(length=128), nullable=False)
    op.alter_column("educational_redactor", "firstName", existing_type=sa.VARCHAR(length=128), nullable=False)
    op.alter_column("educational_redactor", "civility", existing_type=sa.VARCHAR(length=20), nullable=False)
