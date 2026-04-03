update
    opening_hours
set
    timespan = ARRAY[numrange(lower(timespan[1]), upper(timespan[2]))]
where
    -- first two conditions should not be needed...
    -- but let's keep things safe:
    -- only two-item timespans with overlapping ranges
    cardinality(timespan) = 2
    and (timespan[1] && timespan[2])
    and "venueId" in (
        4744,
        11153,
        18359,
        79835,
        104542,
        109056,
        144154,
        151824,
        152133
    )
returning
    id, "venueId", weekday, timespan
;
