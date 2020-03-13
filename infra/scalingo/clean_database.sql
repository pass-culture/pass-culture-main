DO $$ DECLARE
  r RECORD;
BEGIN
  FOR r IN (SELECT pg_proc.oid::regprocedure FROM pg_proc join pg_roles on pg_proc.proowner = pg_roles.oid WHERE pronamespace = 'public'::regnamespace AND rolname = (SELECT current_user from current_user )) LOOP
    EXECUTE 'DROP FUNCTION ' || r.oid || ' CASCADE';
  END LOOP;
END $$;


DO $$ DECLARE
  r RECORD;
BEGIN
  FOR r IN (SELECT cfgname from pg_ts_config join pg_roles on pg_ts_config.cfgowner = pg_roles.oid where rolname = (SELECT current_user from current_user )) LOOP
    EXECUTE 'DROP TEXT SEARCH CONFIGURATION  ' || r.cfgname || ' CASCADE';
  END LOOP;
END $$;


DO $$ DECLARE
  r RECORD;
BEGIN
  FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tableowner != 'admin_patroni') LOOP
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
      AND t.typname not like 'gbtree%'
      AND pg_catalog.pg_type_is_visible(t.oid)
      AND t.typowner not in (SELECT oid FROM pg_catalog.pg_roles WHERE rolname like 'admin_patroni')
  ) LOOP
    EXECUTE 'DROP TYPE IF EXISTS ' || quote_ident(r.typename) || ' CASCADE';
  END LOOP;
END $$;