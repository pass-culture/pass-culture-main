"""Delete table user_pro_new_nav_state used for beta and A/B testing during new pro frontend deployment"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2d723bb0c686"
down_revision = "7356bdbfd295"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS user_pro_new_nav_state;")


def downgrade() -> None:
    op.execute(
        """CREATE TABLE IF NOT EXISTS user_pro_new_nav_state (
        id BIGSERIAL NOT NULL,
        "userId" BIGINT NOT NULL,
        "eligibilityDate" TIMESTAMP WITHOUT TIME ZONE,
        "newNavDate" TIMESTAMP WITHOUT TIME ZONE,
        PRIMARY KEY (id),
        FOREIGN KEY("userId") REFERENCES "user" (id) ON DELETE CASCADE,
        UNIQUE ("userId")
        );"""
    )
