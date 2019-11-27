CREATE OR REPLACE FUNCTION create_recommendations(max_rows INTEGER default 1000000)
RETURNS VOID AS $$
DECLARE
  now TIMESTAMP;
  now_plus_ten_days TIMESTAMP;
BEGIN
  SET session_replication_role = replica; -- Désactivation des triggers
  SELECT NOW() INTO now;
  SELECT now - INTERVAL '10 days' INTO now_plus_ten_days;

  FOR counter IN 1..max_rows BY 10 LOOP
    INSERT INTO "recommendation" ("userId", "dateCreated", "dateUpdated", "isClicked", "isFirst")
    VALUES
    (1, now_plus_ten_days, now_plus_ten_days, TRUE, FALSE),
    (1, now_plus_ten_days, now_plus_ten_days, TRUE, FALSE),
    (1, now_plus_ten_days, now_plus_ten_days, TRUE, FALSE),
    (1, now_plus_ten_days, now_plus_ten_days, TRUE, FALSE),
    (1, now_plus_ten_days, now_plus_ten_days, TRUE, FALSE),
    (1, now_plus_ten_days, now_plus_ten_days, TRUE, FALSE),
    (1, now_plus_ten_days, now_plus_ten_days, TRUE, FALSE),
    (1, now_plus_ten_days, now_plus_ten_days, TRUE, FALSE),
    (1, now_plus_ten_days, now_plus_ten_days, TRUE, FALSE),
    (1, now_plus_ten_days, now_plus_ten_days, TRUE, FALSE);
  END LOOP;

  RETURN;
END;
$$ LANGUAGE plpgsql;