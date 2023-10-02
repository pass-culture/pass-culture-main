"""add start/end dates to collective offer templates"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "5c1e763e65d9"
down_revision = "4205ae20bb32"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "template_start_end_dates",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("start", sa.DateTime(), nullable=False),
        sa.Column("end", sa.DateTime(), nullable=True),
        sa.Column("templateId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["templateId"], ["collective_offer_template.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("start", "end", "templateId", name="template_dates_unique_start_end"),
        sa.CheckConstraint('("end" is null) or start < "end"', name="template_dates_start_before_end"),
    )


def downgrade() -> None:
    op.drop_table("template_start_end_dates")
