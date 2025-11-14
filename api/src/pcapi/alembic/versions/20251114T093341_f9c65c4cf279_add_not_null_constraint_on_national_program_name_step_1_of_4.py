"""Add NOT NULL constraint on "national_program.name" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f9c65c4cf279"
down_revision = "5c8418f46c80"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "national_program" DROP CONSTRAINT IF EXISTS "national_program_name_not_null_constraint";
        ALTER TABLE "national_program" ADD CONSTRAINT "national_program_name_not_null_constraint" CHECK ("name" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("national_program_name_not_null_constraint", table_name="national_program")
