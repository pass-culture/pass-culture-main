update booking
set "cancellationLimitDate" = '2025-09-03'
where "stockId" = 332490674
and status = 'CONFIRMED'
and "dateCreated" < '2025-09-01'
;
