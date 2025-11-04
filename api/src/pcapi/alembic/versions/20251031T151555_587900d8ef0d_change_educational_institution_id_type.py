"""change educational_institution id type"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "587900d8ef0d"
down_revision = "442b05ddc75e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.alter_column(
        "educational_institution",
        "id",
        existing_type=sa.INTEGER(),
        type_=sa.BigInteger(),
        existing_nullable=False,
        existing_server_default=sa.text("nextval('educational_institution_id_seq'::regclass)"),
    )


def downgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.alter_column(
        "educational_institution",
        "id",
        existing_type=sa.BigInteger(),
        type_=sa.INTEGER(),
        existing_nullable=False,
        existing_server_default=sa.text("nextval('educational_institution_id_seq'::regclass)"),
    )
