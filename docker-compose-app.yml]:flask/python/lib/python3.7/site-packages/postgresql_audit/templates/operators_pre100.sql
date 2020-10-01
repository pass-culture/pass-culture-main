-- http://schinckel.net/2014/09/29/adding-json%28b%29-operators-to-postgresql/
CREATE OR REPLACE FUNCTION jsonb_subtract(
  "json" jsonb,
  "keys" TEXT[]
)
  RETURNS jsonb
  LANGUAGE SQL
  IMMUTABLE
  STRICT
AS $$
SELECT CASE WHEN "json" ?| "keys" THEN COALESCE(
  (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
     FROM jsonb_each("json")
    WHERE "key" <> ALL ("keys")),
  '{}'
)::jsonb
ELSE "json"
END
$$;

DROP OPERATOR IF EXISTS - (jsonb, text[]);
CREATE OPERATOR - (
  LEFTARG = jsonb,
  RIGHTARG = text[],
  PROCEDURE = jsonb_subtract
);
