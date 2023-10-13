"""Set mediation.authorId as null when user is deleted 1/2
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d968ffd57c40"
down_revision = "b397aa305b2e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("mediation_authorId_fkey", "mediation", type_="foreignkey")
    op.create_foreign_key(
        "mediation_authorId_fkey",
        "mediation",
        "user",
        ["authorId"],
        ["id"],
        ondelete="SET NULL",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("mediation_authorId_fkey", "mediation", type_="foreignkey")
    op.create_foreign_key(
        "mediation_authorId_fkey", "mediation", "user", ["authorId"], ["id"], postgresql_not_valid=True
    )
