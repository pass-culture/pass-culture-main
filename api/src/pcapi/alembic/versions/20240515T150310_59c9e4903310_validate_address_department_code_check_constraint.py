"""Validate Address.departmentCode check length constraint"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "59c9e4903310"
down_revision = "b647a8e48fb5"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""ALTER TABLE address VALIDATE CONSTRAINT "address_departmentCode_check" """)


def downgrade() -> None:
    # Nothing to downgrade
    pass
