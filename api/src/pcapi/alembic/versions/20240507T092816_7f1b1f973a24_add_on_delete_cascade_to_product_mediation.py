"""
add on delete cascade to product_mediation table
"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "7f1b1f973a24"
down_revision = "ba7542f1fa64"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("product_mediation_productId_fkey", "product_mediation", type_="foreignkey")
    op.create_foreign_key(
        "product_mediation_productId_fkey",
        "product_mediation",
        "product",
        ["productId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )
    # post migration b40706d45035 should be run after this migration in order to validate the constraint


def downgrade() -> None:
    op.drop_constraint("product_mediation_productId_fkey", "product_mediation", type_="foreignkey")
    op.create_foreign_key(
        "product_mediation_productId_fkey",
        "product_mediation",
        "product",
        ["productId"],
        ["id"],
        postgresql_not_valid=True,
    )
    # post migration b40706d45035 dowgrade should be run after this migration in order to validate the constraint
