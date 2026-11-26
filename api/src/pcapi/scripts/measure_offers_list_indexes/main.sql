-- One time script to measure the cost of the offers list indexes (PR pass-culture-main#24929), run before and after each index

SELECT now(), version();

\echo 'Counters reset dates: they must not change between two measures'
SELECT now(), stats_reset FROM pg_stat_database WHERE datname = current_database();
SELECT now(), dealloc, stats_reset FROM pg_stat_statements_info;

\echo 'Phase 1: offer writes'
SELECT now(), lower(split_part(query, ' ', 1)) AS command, sum(calls) AS calls, round(sum(total_exec_time)::numeric) AS total_ms
FROM pg_stat_statements
WHERE query ~* '^(insert into|update|delete from) "?offer"? '
GROUP BY 2
ORDER BY 2;

\echo 'Phase 1: stock writes'
SELECT now(), lower(split_part(query, ' ', 1)) AS command, sum(calls) AS calls, round(sum(total_exec_time)::numeric) AS total_ms
FROM pg_stat_statements
WHERE query ~* '^(insert into|update|delete from) "?stock"? '
GROUP BY 2
ORDER BY 2;

\echo 'Phase 1: booking writes (control table, without new index)'
SELECT now(), lower(split_part(query, ' ', 1)) AS command, sum(calls) AS calls, round(sum(total_exec_time)::numeric) AS total_ms
FROM pg_stat_statements
WHERE query ~* '^(insert into|update|delete from) "?booking"? '
GROUP BY 2
ORDER BY 2;

\echo 'Phase 1: WAL volume'
SELECT now(), wal_bytes, pg_size_pretty(wal_bytes) AS wal_size, stats_reset
FROM pg_stat_wal;

\echo 'Phase 2: offer indexes'
SELECT now(), s.indexrelname AS index_name,
    pg_size_pretty(pg_relation_size(s.indexrelid)) AS size,
    s.idx_scan,
    to_jsonb(s) ->> 'last_idx_scan' AS last_idx_scan,  -- only exists from PostgreSQL 16
    i.indisprimary OR i.indisunique AS is_unique
FROM pg_stat_user_indexes s
JOIN pg_index i ON i.indexrelid = s.indexrelid
WHERE s.relname = 'offer'
ORDER BY pg_relation_size(s.indexrelid) DESC;

\echo 'Phase 2: stock indexes'
SELECT now(), s.indexrelname AS index_name,
    pg_size_pretty(pg_relation_size(s.indexrelid)) AS size,
    s.idx_scan,
    to_jsonb(s) ->> 'last_idx_scan' AS last_idx_scan,  -- only exists from PostgreSQL 16
    i.indisprimary OR i.indisunique AS is_unique
FROM pg_stat_user_indexes s
JOIN pg_index i ON i.indexrelid = s.indexrelid
WHERE s.relname = 'stock'
ORDER BY pg_relation_size(s.indexrelid) DESC;
