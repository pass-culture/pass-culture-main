"""
create_table_favories_adage_offer
"""
from alembic import op
import sqlalchemy as sa


revision = "2d57a58abc38"
down_revision = "1112f930c271"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "adage_favorite_offer_template",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("educationalRedactor", sa.String(length=30), nullable=False),
        sa.Column("offerTemplateId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["offerTemplateId"], ["collective_offer_template.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("educationalRedactor"),
    )
    op.create_table(
        "adage_favorite_offer",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("educationalRedactor", sa.String(length=30), nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["offerId"], ["collective_offer.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("educationalRedactor"),
    )


def downgrade() -> None:
    op.drop_table("adage_favorite_offer")
    op.drop_table("adage_favorite_offer_template")
