"""create_template_offer_table
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "e289b8d9cbe9"
down_revision = "24321401ffaa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "collective_offer_template",
        sa.Column("audioDisabilityCompliant", sa.Boolean(), nullable=True),
        sa.Column("mentalDisabilityCompliant", sa.Boolean(), nullable=True),
        sa.Column("motorDisabilityCompliant", sa.Boolean(), nullable=True),
        sa.Column("visualDisabilityCompliant", sa.Boolean(), nullable=True),
        sa.Column("lastValidationDate", sa.DateTime(), nullable=True),
        sa.Column(
            "validation",
            postgresql.ENUM("APPROVED", "DRAFT", "PENDING", "REJECTED", name="validation_status", create_type=False),
            server_default="APPROVED",
            nullable=False,
        ),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=True),
        sa.Column("isActive", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=140), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("durationMinutes", sa.Integer(), nullable=True),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.Column("subcategoryId", sa.Text(), nullable=False),
        sa.Column("dateUpdated", sa.DateTime(), nullable=True),
        sa.Column(
            "students",
            postgresql.ARRAY(
                postgresql.ENUM(
                    "COLLEGE4",
                    "COLLEGE3",
                    "CAP1",
                    "CAP2",
                    "GENERAL2",
                    "GENERAL1",
                    "GENERAL0",
                    name="studentlevels",
                    create_type=False,
                )
            ),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("priceDetail", sa.Text(), nullable=True),
        sa.Column("bookingEmail", sa.String(length=120), nullable=True),
        sa.Column("contactEmail", sa.String(length=120), nullable=False),
        sa.Column("contactPhone", sa.String(length=20), nullable=False),
        sa.Column("jsonData", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(
            ["venueId"],
            ["venue.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_collective_offer_template_lastValidationDate"),
        "collective_offer_template",
        ["lastValidationDate"],
        unique=False,
    )
    op.create_index(
        op.f("ix_collective_offer_template_subcategoryId"), "collective_offer_template", ["subcategoryId"], unique=False
    )
    op.create_index(
        op.f("ix_collective_offer_template_validation"), "collective_offer_template", ["validation"], unique=False
    )
    op.create_index(
        op.f("ix_collective_offer_template_venueId"), "collective_offer_template", ["venueId"], unique=False
    )


def downgrade() -> None:
    op.drop_table("collective_offer_template")
