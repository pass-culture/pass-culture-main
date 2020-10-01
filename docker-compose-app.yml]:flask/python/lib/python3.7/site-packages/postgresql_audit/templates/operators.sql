-- http://coussej.github.io/2016/05/24/A-Minus-Operator-For-PostgreSQLs-JSONB/
CREATE OR REPLACE FUNCTION jsonb_subtract(arg1 jsonb, arg2 jsonb)
RETURNS jsonb AS $$
SELECT
  COALESCE(json_object_agg(key, value), '{}')::jsonb
FROM
  jsonb_each(arg1)
WHERE
  (arg1 -> key) <> (arg2 -> key) OR (arg2 -> key) IS NULL
$$ LANGUAGE SQL;

DROP OPERATOR IF EXISTS - (jsonb, jsonb);

CREATE OPERATOR - (
  LEFTARG = jsonb,
  RIGHTARG = jsonb,
  PROCEDURE = jsonb_subtract
);
