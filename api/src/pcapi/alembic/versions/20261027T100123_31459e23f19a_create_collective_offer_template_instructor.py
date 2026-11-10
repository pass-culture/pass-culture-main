"""Create CollectiveOfferTemplateInstructor"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "31459e23f19a"
down_revision = "224c7a7ce18d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "collective_offer_template_instructor",
        sa.Column("instructorId", sa.BigInteger(), nullable=False),
        sa.Column("collectiveOfferTemplateId", sa.BigInteger(), nullable=False),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("collectiveOfferTemplateId", name="unique_instructor_per_collective_offer_template"),
    )
    op.create_foreign_key(
        "collective_offer_template_instructor_instructorId_fkey",
        "collective_offer_template_instructor",
        "user",
        ["instructorId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )
    op.create_foreign_key(
        "collective_offer_template_instructor_collectiveTemplateId_fkey",
        "collective_offer_template_instructor",
        "collective_offer_template",
        ["collectiveOfferTemplateId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )
    op.create_index(
        op.f("ix_collective_offer_template_instructor_collectiveOfferTemplateId"),
        "collective_offer_template_instructor",
        ["collectiveOfferTemplateId"],
        unique=False,
    )
    op.create_index(
        op.f("ix_collective_offer_template_instructor_instructorId"),
        "collective_offer_template_instructor",
        ["instructorId"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("collective_offer_template_instructor")
