"""Create table orphan_dms_application
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5507ba019ce1"
down_revision = "4e4384ac4c8f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "orphan_dms_application",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("application_id", sa.BigInteger(), nullable=False),
        sa.Column("process_id", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", "application_id"),
    )
    op.create_index(op.f("ix_orphan_dms_application_email"), "orphan_dms_application", ["email"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_orphan_dms_application_email"), table_name="orphan_dms_application")
    op.drop_table("orphan_dms_application")
