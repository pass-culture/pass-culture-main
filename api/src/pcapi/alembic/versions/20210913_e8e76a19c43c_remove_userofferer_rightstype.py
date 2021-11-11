"""Remove UserOfferer.rights"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e8e76a19c43c"
down_revision = "d9a21d14e3ae"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("user_offerer", "rights")
    op.execute("DROP TYPE IF EXISTS rightstype")


def downgrade():
    # Even if we rollback, we're not going to use the `rights` column.
    # Restoring the custom type would be cumbersome and useless, so we
    # just make it a `TEXT` column.
    op.add_column(
        "user_offerer",
        sa.Column("rights", sa.Text(), nullable=True),
    )
