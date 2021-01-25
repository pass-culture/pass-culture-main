"""Add foreign key on product.owningOffererId (Step 1/2)

Revision ID: e8ba63242789
Revises: 539a0d1a86d0
Create Date: 2021-01-25 14:46:15.963266

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "e8ba63242789"
down_revision = "539a0d1a86d0"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            ALTER TABLE "product"
            ADD CONSTRAINT product_owning_offerer_id_fkey
            FOREIGN KEY ("owningOffererId")
            REFERENCES offerer(id)
            NOT VALID;
        """
    )


def downgrade():
    op.drop_constraint("product_owning_offerer_id_fkey", "product")
