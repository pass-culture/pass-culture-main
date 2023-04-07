"""Remove old offerer/venue search indexes"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "515b8245129f"
down_revision = "4b5ddbcf6b11"
branch_labels = None
depends_on = None


INDEXES = (
    "idx_offerer_fts_address",
    "idx_offerer_fts_name",
    "idx_offerer_fts_siret",
    "idx_venue_fts_address",
    "idx_venue_fts_city",
    "idx_venue_fts_name",
    "idx_venue_fts_publicName",
    "idx_venue_fts_siret",
)

CREATE_STATEMENTS = (
    "CREATE INDEX CONCURRENTLY idx_offerer_fts_address ON public.offerer USING gin (to_tsvector('public.french_unaccent'::regconfig, (address)::text))",
    "CREATE INDEX CONCURRENTLY idx_offerer_fts_name ON public.offerer USING gin (to_tsvector('public.french_unaccent'::regconfig, (name)::text))",
    "CREATE INDEX CONCURRENTLY idx_offerer_fts_siret ON public.offerer USING gin (to_tsvector('public.french_unaccent'::regconfig, (siren)::text))",
    "CREATE INDEX CONCURRENTLY idx_venue_fts_address ON public.venue USING gin (to_tsvector('public.french_unaccent'::regconfig, (address)::text))",
    "CREATE INDEX CONCURRENTLY idx_venue_fts_city ON public.venue USING gin (to_tsvector('public.french_unaccent'::regconfig, (city)::text))",
    "CREATE INDEX CONCURRENTLY idx_venue_fts_name ON public.venue USING gin (to_tsvector('public.french_unaccent'::regconfig, (name)::text))",
    """CREATE INDEX CONCURRENTLY "idx_venue_fts_publicName" ON public.venue USING gin (to_tsvector('public.french_unaccent'::regconfig, ("publicName")::text))""",
    "CREATE INDEX CONCURRENTLY idx_venue_fts_siret ON public.venue USING gin (to_tsvector('public.french_unaccent'::regconfig, (siret)::text))",
)


def upgrade() -> None:
    # We need to commit the transaction, because `DROP INDEX
    # CONCURRENTLY` cannot run inside a transaction.
    op.execute("COMMIT")
    for index in INDEXES:
        op.execute(f'drop index concurrently if exists "{index}"')


def downgrade() -> None:
    # We need to commit the transaction, because `DROP INDEX
    # CONCURRENTLY` cannot run inside a transaction.
    op.execute("COMMIT")
    for statement in CREATE_STATEMENTS:
        op.execute(statement)
