"""Set BO permission to move collective offer"""

from alembic import op
from sqlalchemy.sql import text


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2cb08c3a175a"
down_revision = "058c27483eab"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        text("""
        INSERT INTO permission (name)
        VALUES ('MOVE_COLLECTIVE_OFFER')
        ON CONFLICT (name) DO NOTHING;
    """)
    )
    op.execute(
        text("""
        INSERT INTO role_permission ("roleId", "permissionId")
        SELECT role.id, permission.id
        FROM permission, role
        WHERE permission.name = 'MOVE_COLLECTIVE_OFFER'
        AND role.name LIKE 'support_pro%'
        ON CONFLICT ("roleId", "permissionId") DO NOTHING;
    """)
    )


def downgrade() -> None:
    pass
