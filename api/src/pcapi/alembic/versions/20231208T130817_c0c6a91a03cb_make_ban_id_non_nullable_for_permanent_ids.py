"""
Check that Ban ID is not null for permanent venues
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c0c6a91a03cb"
down_revision = "faed981725fd"
branch_labels = None
depends_on = None


CONSTRAINT_CHECK_IS_PERMANENT_AND_HAS_BAN_ID_OR_IS_VIRTUAL = """
    ("isPermanent" IS FALSE)
    OR ("isVirtual" IS True) 
    OR ("isPermanent" IS TRUE AND "isVirtual" IS FALSE AND "banId" IS NOT NULL)
"""


def upgrade() -> None:
    op.create_check_constraint(
        constraint_name="check_non_virtual_permanent_venues_have_ban_id",
        table_name="venue",
        condition=(CONSTRAINT_CHECK_IS_PERMANENT_AND_HAS_BAN_ID_OR_IS_VIRTUAL),
    )


def downgrade() -> None:
    op.drop_constraint("check_non_virtual_permanent_venues_have_ban_id", "venue", type_="check")
