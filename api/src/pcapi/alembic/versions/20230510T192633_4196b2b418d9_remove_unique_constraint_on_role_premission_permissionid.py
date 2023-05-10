"""remove unique constraint on role_premission.permissionId"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "4196b2b418d9"
down_revision = "ddd0895ce8c6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("role_permission_roleId_permissionId_key", "role_permission", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint(
        "role_permission_roleId_permissionId_key", "role_permission", ["roleId", "permissionId"]
    )
