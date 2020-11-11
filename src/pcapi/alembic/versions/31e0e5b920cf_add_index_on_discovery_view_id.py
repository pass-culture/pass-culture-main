"""add_index_on_discovery_view_id

Revision ID: 31e0e5b920cf
Revises: 0a86df88b8f8
Create Date: 2020-07-01 10:03:59.944036

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "31e0e5b920cf"
down_revision = "0a86df88b8f8"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.create_index(op.f("idx_discovery_view_offerId"), "discovery_view", ["id"], postgresql_concurrently=True)
    op.create_index(op.f("idx_discovery_view_v3_offerId"), "discovery_view_v3", ["id"], postgresql_concurrently=True)


def downgrade():
    op.drop_index("idx_discovery_view_offerId", table_name="discovery_view")
    op.drop_index("idx_discovery_view_v3_offerId", table_name="discovery_view_v3")
