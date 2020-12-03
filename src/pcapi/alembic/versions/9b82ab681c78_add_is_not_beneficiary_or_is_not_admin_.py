"""add_is_not_beneficiary_or_is_not_admin_constraint

Revision ID: 9b82ab681c78
Revises: df15599370fd
Create Date: 2020-12-03 16:19:32.479400

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9b82ab681c78"
down_revision = "df15599370fd"
branch_labels = None
depends_on = None


def upgrade():
    # we need to drop this constraint since cannot_book_free_offers column is not deleted yet
    # and its default value is true so the sandbox could not be loaded
    op.drop_constraint("check_admin_cannot_book_free_offers", "user")

    op.create_check_constraint(
        constraint_name="check_admin_is_not_beneficiary",
        table_name="user",
        condition='"isBeneficiary" IS FALSE OR "isAdmin" IS FALSE',
    )


def downgrade():
    op.drop_constraint("check_admin_is_not_beneficiary", "user")
