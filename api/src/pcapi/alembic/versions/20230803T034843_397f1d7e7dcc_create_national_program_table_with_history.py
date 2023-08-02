"""create national program table (with history)
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "397f1d7e7dcc"
down_revision = "b5652ab2625c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create national program
    op.create_table(
        "national_program",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Create collective offer template links history
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

    # Create collective offer links history
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

    # New column (collective offer): nationalProgramId
    op.add_column("collective_offer", sa.Column("nationalProgramId", sa.BigInteger(), nullable=True))
    op.create_index(
        op.f("ix_collective_offer_nationalProgramId"), "collective_offer", ["nationalProgramId"], unique=False
    )
    op.create_foreign_key(None, "collective_offer", "national_program", ["nationalProgramId"], ["id"])

    # New column (collective offer template): nationalProgramId
    op.add_column("collective_offer_template", sa.Column("nationalProgramId", sa.BigInteger(), nullable=True))
    op.create_index(
        op.f("ix_collective_offer_template_nationalProgramId"),
        "collective_offer_template",
        ["nationalProgramId"],
        unique=False,
    )
    op.create_foreign_key(None, "collective_offer_template", "national_program", ["nationalProgramId"], ["id"])


def downgrade() -> None:
    op.drop_column("collective_offer", "nationalProgramId")
    op.drop_column("collective_offer_template", "nationalProgramId")

    op.drop_table("national_program_offer_link_history")
    op.drop_table("national_program_offer_template_link_history")
    op.drop_table("national_program")
