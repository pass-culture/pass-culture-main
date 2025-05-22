"""Create unique constraint uuid on product_mediation"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "03fe9009ff8e"
down_revision = "bbe4eaf21da3"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            ALTER TABLE product_mediation ADD CONSTRAINT product_mediation_uuid_key UNIQUE USING INDEX ix_product_mediation_uuid;
            """
        ),
    )


def downgrade() -> None:
    op.execute(""" ALTER TABLE "product_mediation" DROP CONSTRAINT "product_mediation_uuid_key" """)
