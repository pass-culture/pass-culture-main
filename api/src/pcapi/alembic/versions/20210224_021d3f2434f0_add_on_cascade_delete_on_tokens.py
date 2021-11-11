"""Add on cascade delete on tokens

Revision ID: 021d3f2434f0
Revises: b00c0a0dec8f
Create Date: 2021-02-24 16:37:59.422400

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "021d3f2434f0"
down_revision = "b00c0a0dec8f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
    ALTER TABLE ONLY public.token
    DROP CONSTRAINT "token_userId_fkey",
    ADD CONSTRAINT "token_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id) ON DELETE CASCADE;
    """
    )


def downgrade() -> None:
    op.execute(
        """
    ALTER TABLE ONLY public.token
    DROP CONSTRAINT "token_userId_fkey",
    ADD CONSTRAINT "token_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id);
    """
    )
