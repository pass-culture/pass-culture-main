"""create_table_CollectiveOfferRequest
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "9793c2c38cb5"
down_revision = "1a27ac9f25a2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "collective_offer_request",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("phoneNumber", sa.String(length=30), nullable=True),
        sa.Column("requestedDate", sa.Date(), nullable=True),
        sa.Column("totalStudents", sa.Integer(), nullable=True),
        sa.Column("totalTeachers", sa.Integer(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("collectiveOfferTemplateId", sa.BigInteger(), nullable=False),
        sa.Column("educationalInstitutionId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["collectiveOfferTemplateId"],
            ["collective_offer_template.id"],
        ),
        sa.ForeignKeyConstraint(
            ["educationalInstitutionId"],
            ["educational_institution.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_collective_offer_request_collectiveOfferTemplateId"),
        "collective_offer_request",
        ["collectiveOfferTemplateId"],
        unique=False,
    )
    op.create_index(
        op.f("ix_collective_offer_request_educationalInstitutionId"),
        "collective_offer_request",
        ["educationalInstitutionId"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("collective_offer_request")
