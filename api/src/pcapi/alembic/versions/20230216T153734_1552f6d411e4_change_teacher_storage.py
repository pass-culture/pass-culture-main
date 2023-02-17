"""change_teacher_storage
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1552f6d411e4"
down_revision = "0272ad68e89d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("collective_offer", sa.Column("teacherId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_collective_offer_teacherId"), "collective_offer", ["teacherId"], unique=False)
    op.create_foreign_key(
        "collectiveBooking_educationalRedactor_fkey", "collective_offer", "educational_redactor", ["teacherId"], ["id"]
    )
    op.drop_column("collective_offer", "teacherEmail")


def downgrade() -> None:
    op.add_column("collective_offer", sa.Column("teacherEmail", sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_constraint("collectiveBooking_educationalRedactor_fkey", "collective_offer", type_="foreignkey")
    op.drop_index(op.f("ix_collective_offer_teacherId"), table_name="collective_offer")
    op.drop_column("collective_offer", "teacherId")
