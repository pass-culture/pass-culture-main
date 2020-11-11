"""Index Recommendation.isFavorite

Revision ID: 5c79b8845ffe
Revises: 5f072f461580
Create Date: 2018-09-20 08:07:16.320880

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "5c79b8845ffe"
down_revision = "5f072f461580"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f("ix_recommendation_isFavorite"), "recommendation", ["isFavorite"], unique=False)


def downgrade():
    op.drop_index("ix_recommendation_isFavorite", table_name="recommendation")
