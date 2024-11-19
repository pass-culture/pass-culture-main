"""add uuid column to product mediation"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "c05644202f3d"
down_revision = "f670bc320b96"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("product_mediation", sa.Column("uuid", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("product_mediation", "uuid")
