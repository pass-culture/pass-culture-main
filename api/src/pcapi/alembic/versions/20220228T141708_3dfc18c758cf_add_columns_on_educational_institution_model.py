"""add_columns_on_educational_institution_model
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3dfc18c758cf"
down_revision = "cc59756a1974"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("educational_institution", sa.Column("city", sa.Text(), nullable=True))
    op.add_column("educational_institution", sa.Column("email", sa.Text(), nullable=True))
    op.add_column("educational_institution", sa.Column("name", sa.Text(), nullable=True))
    op.add_column("educational_institution", sa.Column("phoneNumber", sa.String(length=30), nullable=True))
    op.add_column("educational_institution", sa.Column("postalCode", sa.String(length=10), nullable=True))


def downgrade():
    op.drop_column("educational_institution", "postalCode")
    op.drop_column("educational_institution", "phoneNumber")
    op.drop_column("educational_institution", "name")
    op.drop_column("educational_institution", "email")
    op.drop_column("educational_institution", "city")
