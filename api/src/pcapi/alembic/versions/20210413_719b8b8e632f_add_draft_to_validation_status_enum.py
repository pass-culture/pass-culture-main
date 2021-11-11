from alembic import op


# revision identifiers, used by Alembic.
revision = "719b8b8e632f"
down_revision = "87dbafddbf19"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE validation_status ADD VALUE 'DRAFT'")


def downgrade():
    op.execute("ALTER TYPE validation_status RENAME TO validation_status_to_drop")
    op.execute("CREATE TYPE validation_status AS ENUM ('APPROVED', 'AWAITING', 'REJECTED')")
    op.alter_column("offer", "validation", server_default=None)
    op.execute(
        (
            'ALTER TABLE offer ALTER COLUMN "validation" TYPE validation_status USING '
            '"validation"::text::validation_status'
        )
    )
    op.alter_column("offer", "validation", server_default="APPROVED")
    op.execute("DROP TYPE validation_status_to_drop")
