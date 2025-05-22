"""Add Address.departmentCode column"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b647a8e48fb5"
down_revision = "67f667caea27"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("address", sa.Column("departmentCode", sa.Text(), nullable=True))
    op.execute(
        """ALTER TABLE address ADD CONSTRAINT "address_departmentCode_check" CHECK (length("departmentCode") = 2 OR length("departmentCode") = 3) NOT VALID"""
    )

    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_address_departmentCode"),
            "address",
            ["departmentCode"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_address_departmentCode"), table_name="address", postgresql_concurrently=True, if_exists=True
        )
    op.drop_column("address", "departmentCode")
