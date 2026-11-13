-- One time script to check the indexes being created and the invalid indexes

SELECT pid, phase, blocks_done, blocks_total
FROM pg_stat_progress_create_index;

SELECT c.relname
FROM pg_index i
JOIN pg_class c ON c.oid = i.indexrelid
WHERE NOT i.indisvalid;
