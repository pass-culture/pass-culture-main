"""Add NOT NULL constraint on "national_program.name" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "eb6ac3ba2c6a"
down_revision = "d3b824e330dc"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("national_program_name_not_null_constraint", table_name="national_program")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "national_program" ADD CONSTRAINT "national_program_name_not_null_constraint" CHECK ("name" IS NOT NULL) NOT VALID"""
    )
