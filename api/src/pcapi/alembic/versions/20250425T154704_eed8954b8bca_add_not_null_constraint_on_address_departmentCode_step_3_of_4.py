"""
Add NOT NULL constraint on "address.departmentCode" (step 3 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "eed8954b8bca"
down_revision = "1dd69b99a36d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("address", "departmentCode", nullable=False)


def downgrade() -> None:
    op.alter_column("address", "departmentCode", nullable=True)
