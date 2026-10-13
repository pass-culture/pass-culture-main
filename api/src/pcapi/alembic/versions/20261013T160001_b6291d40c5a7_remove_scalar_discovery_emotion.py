"""Remove the old scalar discovery emotion after deploying array support."""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
revision = "b6291d40c5a7"
down_revision = "1df78b3694c2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("check_discovery_emotion", "discovery", type_="check")
    op.drop_column("discovery", "emotion")
    op.execute("ALTER TABLE discovery VALIDATE CONSTRAINT check_discovery_emotions")


def downgrade() -> None:
    op.add_column("discovery", sa.Column("emotion", sa.Text(), nullable=True))
    op.create_check_constraint(
        "check_discovery_emotion",
        "discovery",
        "emotion IN ('intrigu\u00e9', '\u00e9merveill\u00e9', 'touch\u00e9', 'surpris', 'bouscul\u00e9', 'indiff\u00e9rent')",
    )
    op.execute("UPDATE discovery SET emotion = emotions[1] WHERE emotions IS NOT NULL AND cardinality(emotions) > 0")
