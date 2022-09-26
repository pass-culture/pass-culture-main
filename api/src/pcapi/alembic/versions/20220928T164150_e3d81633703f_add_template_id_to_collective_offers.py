"""add_template_id_to_collective_offers
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "e3d81633703f"
down_revision = "0ba4beee498d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("collective_offer", sa.Column("templateId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_collective_offer_templateId"), "collective_offer", ["templateId"], unique=False)
    op.create_foreign_key(
        "collective_offer_template_fkey", "collective_offer", "collective_offer_template", ["templateId"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("collective_offer_template_fkey", "collective_offer", type_="foreignkey")
    op.drop_index(op.f("ix_collective_offer_templateId"), table_name="collective_offer")
    op.drop_column("collective_offer", "templateId")
