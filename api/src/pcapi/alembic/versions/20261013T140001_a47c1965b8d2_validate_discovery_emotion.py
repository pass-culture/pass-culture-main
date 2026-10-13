"""Validate the discovery emotion constraint after deployment."""

from alembic import op


# pre/post deployment: post
revision = "a47c1965b8d2"
down_revision = "9a712e6bd430"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE discovery VALIDATE CONSTRAINT check_discovery_emotion")


def downgrade() -> None:
    op.drop_constraint("check_discovery_emotion", "discovery", type_="check")
    op.create_check_constraint(
        "check_discovery_emotion",
        "discovery",
        "emotion IN ('intrigu\u00e9', '\u00e9merveill\u00e9', 'touch\u00e9', 'surpris', 'bouscul\u00e9', 'indiff\u00e9rent')",
        postgresql_not_valid=True,
    )
