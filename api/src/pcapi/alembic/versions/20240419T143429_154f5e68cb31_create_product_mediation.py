"""
create product_mediation table that will store the image url of the product
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from pcapi.core.offers.models import ImageType
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "154f5e68cb31"
down_revision = "d1767ee2dac1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement;")
    op.create_table(
        "product_mediation",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("idAtProviders", sa.String(length=70), nullable=True),
        sa.Column("dateModifiedAtLastProvider", sa.DateTime(), nullable=True),
        sa.Column("fieldsUpdated", postgresql.ARRAY(sa.String(length=100)), server_default="{}", nullable=False),
        sa.Column("productId", sa.BigInteger(), nullable=False),
        sa.Column("url", sa.String(length=255), nullable=False),
        sa.Column("imageType", MagicEnum(ImageType), nullable=False),
        sa.Column("lastProviderId", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["lastProviderId"],
            ["provider.id"],
        ),
        sa.ForeignKeyConstraint(
            ["productId"],
            ["product.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idAtProviders"),
        sa.UniqueConstraint("url"),
    )

    op.execute("select 1 -- squawk:ignore-next-statement;")  # the table is empty, doesn't need to block writes
    op.create_index(op.f("ix_product_mediation_productId"), "product_mediation", ["productId"], unique=False)


def downgrade() -> None:
    op.drop_table("product_mediation")
