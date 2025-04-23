"""Create index on venue.departementCode"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1be3db2bd7b9"
down_revision = "2eee70a08b61"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_venue_departementCode"),
            "venue",
            ["departementCode"],
            unique=False,
            if_not_exists=True,
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_venue_departementCode"), table_name="venue", if_exists=True, postgresql_concurrently=True
        )
