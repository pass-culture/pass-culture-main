"""
create_table_CollectiveOfferEducationalRedactor_and_CollectiveOfferTemplateEducationalRedactor
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "eff2f403eaac"
down_revision = "1112f930c271"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "collective_offer_template_educational_redactor",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("educationalRedactorId", sa.BigInteger(), nullable=False),
        sa.Column("collectiveOfferTemplateId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["collectiveOfferTemplateId"],
            ["collective_offer_template.id"],
        ),
        sa.ForeignKeyConstraint(
            ["educationalRedactorId"],
            ["educational_redactor.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("educationalRedactorId", "collectiveOfferTemplateId", name="unique_redactorId_template"),
    )
    op.create_table(
        "collective_offer_educational_redactor",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("educationalRedactorId", sa.BigInteger(), nullable=False),
        sa.Column("collectiveOfferId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["collectiveOfferId"],
            ["collective_offer.id"],
        ),
        sa.ForeignKeyConstraint(
            ["educationalRedactorId"],
            ["educational_redactor.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("educationalRedactorId", "collectiveOfferId", name="unique_redactorId_offer"),
    )


def downgrade() -> None:
    op.drop_table("collective_offer_educational_redactor")
    op.drop_table("collective_offer_template_educational_redactor")
