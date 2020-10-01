CREATE OR REPLACE FUNCTION jsonb_subtract(
  "json" jsonb,
  "key_to_remove" TEXT
)
  RETURNS jsonb
  LANGUAGE sql
  IMMUTABLE
  STRICT
AS $$
SELECT CASE WHEN "json" ? "key_to_remove" THEN COALESCE(
  (SELECT ('{' || string_agg(to_json("key")::text || ':' || "value", ',') || '}')
     FROM jsonb_each("json")
    WHERE "key" <> "key_to_remove"),
  '{}'
)::jsonb
ELSE "json"
END
$$;

DROP OPERATOR IF EXISTS - (jsonb, text);
CREATE OPERATOR - (
  LEFTARG = jsonb,
  RIGHTARG = text,
  PROCEDURE = jsonb_subtract
);


CREATE OR REPLACE FUNCTION jsonb_merge(data jsonb, merge_data jsonb)
RETURNS jsonb
IMMUTABLE
LANGUAGE sql
AS $$
    SELECT ('{'||string_agg(to_json(key)||':'||value, ',')||'}')::jsonb
    FROM (
        WITH to_merge AS (
            SELECT * FROM jsonb_each(merge_data)
        )
        SELECT *
        FROM jsonb_each(data)
        WHERE key NOT IN (SELECT key FROM to_merge)
        UNION ALL
        SELECT * FROM to_merge
    ) t;
$$;

DROP OPERATOR IF EXISTS || (jsonb, jsonb);

CREATE OPERATOR || (
  LEFTARG = jsonb,
  RIGHTARG = jsonb,
  PROCEDURE = jsonb_merge
);
