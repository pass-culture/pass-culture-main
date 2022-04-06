"""add_Role_and_Permission_models
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
from pcapi.core.permissions.models import Permissions


revision = "c7877e6119e7"
down_revision = "ce0fcf03be9a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "permission",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=140), nullable=False),
        sa.Column("category", sa.String(length=140), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "role",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=140), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "role_permission",
        sa.Column("role_id", sa.BigInteger(), nullable=True),
        sa.Column("permission_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permission.id"],
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["role.id"],
        ),
    )
    op.execute(
        f"""
        WITH manage_perm(id) AS (
            INSERT INTO permission (name)
            VALUES ('{Permissions.MANAGE_PERMISSIONS.value}')
            RETURNING id
        ), admin_role(id) AS (
            INSERT INTO role (name)
            VALUES ('admin')
            RETURNING id
        )
        INSERT INTO role_permission(role_id, permission_id)
        VALUES (
            (SELECT id FROM admin_role LIMIT 1),
            (SELECT id FROM manage_perm LIMIT 1)
        );
    """
    )


def downgrade():
    op.drop_table("role_permission")
    op.drop_table("role")
    op.drop_table("permission")
