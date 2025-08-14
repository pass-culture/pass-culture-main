update finance_event
set status='ready', "venueId" = 117660, "pricingPointId" = 117660
where id in (41636698, 43595677)
and status = 'pending'
and "venueId" = 117759
;
