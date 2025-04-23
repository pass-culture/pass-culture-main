"""Create user_pro_new_nav_state table for the new pro navbar ab testing and beta testing"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ccd86b897e7a"
down_revision = "17bbd580c848"
branch_labels = None
depends_on = None


def upgrade() -> None:
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


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS user_pro_new_nav_state;")
