"""add formats to collective offers (and templates)
+ subcategoryId becomes nullable (before being removed)"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "2a720f939c92"
down_revision = "45372e34d18c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "collective_offer",
        sa.Column(
            "formats",
            postgresql.ARRAY(sa.Text()),
            nullable=True,
        ),
    )
    op.add_column(
        "collective_offer_template",
        sa.Column(
            "formats",
            postgresql.ARRAY(sa.Text()),
            nullable=True,
        ),
    )

    op.alter_column("collective_offer", "subcategoryId", existing_type=sa.TEXT(), nullable=True)
    op.drop_index("ix_collective_offer_subcategoryId", table_name="collective_offer")
    op.alter_column("collective_offer_template", "subcategoryId", existing_type=sa.TEXT(), nullable=True)
    op.drop_index("ix_collective_offer_template_subcategoryId", table_name="collective_offer_template")


def downgrade() -> None:
    op.create_index(
        "ix_collective_offer_template_subcategoryId", "collective_offer_template", ["subcategoryId"], unique=False
    )
    op.alter_column("collective_offer_template", "subcategoryId", existing_type=sa.TEXT(), nullable=False)
    op.create_index("ix_collective_offer_subcategoryId", "collective_offer", ["subcategoryId"], unique=False)
    op.alter_column("collective_offer", "subcategoryId", existing_type=sa.TEXT(), nullable=False)

    op.drop_column("collective_offer_template", "formats")
    op.drop_column("collective_offer", "formats")
