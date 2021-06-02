"""add_hasIdentityDocumentValidated_to_user

Revision ID: c1bcd8f224b3
Revises: 8bdc4dd58856
Create Date: 2021-06-02 14:54:55.464903

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c1bcd8f224b3"
down_revision = "5bca073597c4"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "user", sa.Column("hasIdentityDocumentValidated", sa.Boolean(), server_default=sa.text("false"), nullable=True)
    )


def downgrade():
    op.drop_column("user", "hasIdentityDocumentValidated")
