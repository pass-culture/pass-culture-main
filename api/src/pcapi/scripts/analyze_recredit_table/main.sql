SELECT
    'Describe table recredit';

\d recredit
SELECT
    'Table stats';

SELECT
    attname,
    null_frac,
    n_distinct,
    most_common_vals :: text,
    most_common_freqs
FROM
    pg_stats
WHERE
    tablename = 'recredit'
    AND attname = 'depositId';

SELECT
    'Update table stats';

ANALYZE VERBOSE recredit;

SELECT
    'Updated table stats';

SELECT
    attname,
    null_frac,
    n_distinct,
    most_common_vals :: text,
    most_common_freqs
FROM
    pg_stats
WHERE
    tablename = 'recredit'
    AND attname = 'depositId';

SELECT
    'New query plan and I/O usage after ANALYZE';

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    recredit."depositId" AS "recredit_depositId",
    recredit."dateCreated" AS "recredit_dateCreated",
    recredit.amount AS recredit_amount,
    recredit."recreditType" AS "recredit_recreditType",
    recredit.comment AS recredit_comment,
    recredit.id AS recredit_id
FROM
    recredit
WHERE
    recredit."depositId" IN (813112, 813096)
ORDER BY
    recredit."dateCreated" DESC;
