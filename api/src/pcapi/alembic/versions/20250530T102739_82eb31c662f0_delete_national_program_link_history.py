"""Delete national_program_offer_link_history and national_program_offer_template_link_history"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "82eb31c662f0"
down_revision = "603c7de2dbce"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_table("national_program_offer_link_history")
    op.drop_table("national_program_offer_template_link_history")


def downgrade() -> None:
    op.create_table(
        "national_program_offer_template_link_history",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.Column("collectiveOfferTemplateId", sa.BigInteger(), nullable=False),
        sa.Column("nationalProgramId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["collectiveOfferTemplateId"], ["collective_offer_template.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["nationalProgramId"], ["national_program.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "national_program_offer_link_history",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.Column("collectiveOfferId", sa.BigInteger(), nullable=False),
        sa.Column("nationalProgramId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["collectiveOfferId"], ["collective_offer.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["nationalProgramId"], ["national_program.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
