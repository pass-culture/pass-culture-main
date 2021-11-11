"""drop_iris_tables

Revision ID: c016332e7bfb
Revises: ffce4944b6b7
Create Date: 2021-08-05 09:48:41.735840

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "c016332e7bfb"
down_revision = "ffce4944b6b7"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP TABLE iris_venues, iris_france;")


def downgrade():
    op.execute(
        """
        CREATE TABLE public.iris_france (
            id bigint NOT NULL,
            "irisCode" character varying(9) NOT NULL,
            centroid public.geometry(Point) NOT NULL,
            shape public.geometry(Geometry,4326) NOT NULL
        );
        """
    )
    op.execute("CREATE SEQUENCE public.iris_france_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;")
    op.execute("ALTER SEQUENCE public.iris_france_id_seq OWNED BY public.iris_france.id;")
    op.execute(
        """
        CREATE TABLE public.iris_venues (
            id bigint NOT NULL,
            "irisId" bigint NOT NULL,
            "venueId" bigint NOT NULL
        );
        """
    )
    op.execute("CREATE SEQUENCE public.iris_venues_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;")
    op.execute("ALTER SEQUENCE public.iris_venues_id_seq OWNED BY public.iris_venues.id;")
    op.execute(
        "ALTER TABLE ONLY public.iris_france ALTER COLUMN id SET DEFAULT nextval('public.iris_france_id_seq'::regclass);"
    )
    op.execute(
        "ALTER TABLE ONLY public.iris_venues ALTER COLUMN id SET DEFAULT nextval('public.iris_venues_id_seq'::regclass);"
    )
    op.execute("SELECT pg_catalog.setval('public.iris_france_id_seq', 1, false);")
    op.execute("SELECT pg_catalog.setval('public.iris_venues_id_seq', 1, false);")
    op.execute("ALTER TABLE ONLY public.iris_france ADD CONSTRAINT iris_france_pkey PRIMARY KEY (id);")
    op.execute("ALTER TABLE ONLY public.iris_venues ADD CONSTRAINT iris_venues_pkey PRIMARY KEY (id);")
    op.execute("CREATE INDEX idx_iris_france_centroid ON public.iris_france USING gist (centroid);")
    op.execute("CREATE INDEX idx_iris_france_shape ON public.iris_france USING gist (shape);")
    op.execute("""CREATE INDEX ix_iris_venues_irisId ON public.iris_venues USING btree ("irisId");""")
    op.execute(
        """ALTER TABLE ONLY public.iris_venues ADD CONSTRAINT "iris_venues_irisId_fkey" FOREIGN KEY ("irisId") REFERENCES public.iris_france(id);"""
    )
    op.execute(
        """ALTER TABLE ONLY public.iris_venues ADD CONSTRAINT "iris_venues_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id);"""
    )
