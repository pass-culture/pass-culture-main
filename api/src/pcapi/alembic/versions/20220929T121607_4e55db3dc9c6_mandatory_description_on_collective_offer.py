"""mandatory_description_on_collective_offer
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "4e55db3dc9c6"
down_revision = "e3d81633703f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "collective_offer",
        "description",
        existing_type=sa.TEXT(),
        nullable=False,
        existing_server_default=sa.text("''::text"),  # type: ignore [arg-type]
    )
    op.alter_column(
        "collective_offer_template",
        "description",
        existing_type=sa.TEXT(),
        nullable=False,
        existing_server_default=sa.text("''::text"),  # type: ignore [arg-type]
    )


def downgrade() -> None:
    op.alter_column(
        "collective_offer_template",
        "description",
        existing_type=sa.TEXT(),
        nullable=True,
        existing_server_default=sa.text("''::text"),  # type: ignore [arg-type]
    )
    op.alter_column(
        "collective_offer",
        "description",
        existing_type=sa.TEXT(),
        nullable=True,
        existing_server_default=sa.text("''::text"),  # type: ignore [arg-type]
    )
