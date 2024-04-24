\set userIds '10,14,15'

insert into "user_pro_new_nav_state" ("userId", "eligibilityDate","newNavDate") 
select "id", NOW(), NULL  
from "user" 
where "user"."id" = ANY(string_to_array(:'userIds', ',')::int[]) 
and not exists (
    select 1 
    from "user_pro_new_nav_state" p 
    where p."userId" = ANY(string_to_array(:'userIds', ',')::int[])
);

update "user_pro_new_nav_state" U 
set "eligibilityDate" = NOW() 
where U."userId" = ANY(string_to_array(:'userIds', ',')::int[]) ;