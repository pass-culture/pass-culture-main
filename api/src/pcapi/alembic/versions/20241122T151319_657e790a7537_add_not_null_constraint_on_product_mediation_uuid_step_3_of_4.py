"""
Add NOT NULL constraint on "product_mediation.uuid" (step 3 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "657e790a7537"
down_revision = "30d1be7a9be4"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("product_mediation", "uuid", nullable=False)


def downgrade() -> None:
    op.alter_column("product_mediation", "uuid", nullable=True)
