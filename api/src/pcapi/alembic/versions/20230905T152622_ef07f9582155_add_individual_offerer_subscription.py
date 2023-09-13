"""Add table: individual_offerer_subscription
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ef07f9582155"
down_revision = "6ad1b6cb8328"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "individual_offerer_subscription",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offererId", sa.BigInteger(), nullable=False),
        sa.Column("isEmailSent", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("dateEmailSent", sa.Date(), nullable=True),
        sa.Column("targetsCollectiveOffers", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("targetsIndividualOffers", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("isCriminalRecordReceived", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("dateCriminalRecordReceived", sa.Date(), nullable=True),
        sa.Column("isCertificateReceived", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("certificateDetails", sa.Text(), nullable=True),
        sa.Column("isExperienceReceived", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("has1yrExperience", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("has5yrExperience", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("isCertificateValid", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.ForeignKeyConstraint(["offererId"], ["offerer.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("offererId"),
    )


def downgrade() -> None:
    op.drop_table("individual_offerer_subscription")
