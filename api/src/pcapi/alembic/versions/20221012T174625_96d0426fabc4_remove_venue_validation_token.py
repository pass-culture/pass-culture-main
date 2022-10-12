"""Remove venue.validationToken"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "96d0426fabc4"
down_revision = "6cdf0c518f89"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("venue", "validationToken")


def downgrade():
    op.add_column("venue", sa.Column("validationToken", sa.VARCHAR(length=27), autoincrement=False, nullable=True))
    op.create_unique_constraint("validation_token_unique_key", "venue", ["validationToken"])
