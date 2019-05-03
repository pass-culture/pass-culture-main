SELECT
    current_status."paymentId"
FROM (
    SELECT
        "paymentId", (array_agg(status ORDER BY date DESC))[1] AS status
    FROM
        payment_status
    GROUP BY
        "paymentId"
) AS current_status
WHERE
    current_status.status = '{{ status }}'
;