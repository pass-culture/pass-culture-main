delete
from action_history
where "actionType" = 'INFO_MODIFIED'
and "venueId" is not null
and comment = 'Synchronisation ADAGE'
and "jsonData"->'modified_info'->'adageId'->>'new_info' = "jsonData"->'modified_info'->'adageId'->>'old_info';

commit;
