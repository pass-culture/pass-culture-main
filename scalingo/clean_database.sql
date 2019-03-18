DO $$ DECLARE
  r RECORD;
BEGIN
  FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
  END LOOP;
END $$;

DO $$ DECLARE
  r RECORD;
BEGIN
  FOR r IN (
    SELECT pg_catalog.format_type(t.oid, NULL) as typename
    FROM pg_catalog.pg_type t
      LEFT JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
    WHERE (t.typrelid = 0 OR (SELECT c.relkind = 'c' FROM pg_catalog.pg_class c WHERE c.oid = t.typrelid))
      AND NOT EXISTS(SELECT 1 FROM pg_catalog.pg_type el WHERE el.oid = t.typelem AND el.typarray = t.oid)
      AND n.nspname = 'public'
      AND pg_catalog.pg_type_is_visible(t.oid)
  ) LOOP
    EXECUTE 'DROP TYPE IF EXISTS ' || quote_ident(r.typename) || ' CASCADE';
  END LOOP;
END $$;