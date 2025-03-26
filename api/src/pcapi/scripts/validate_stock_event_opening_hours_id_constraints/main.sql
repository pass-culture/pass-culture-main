ALTER TABLE stock VALIDATE CONSTRAINT "stock_eventOpeningHoursId_fkey";
ALTER TABLE stock VALIDATE CONSTRAINT "check_stock_with_opening_hours_does_not_have_beginningDatetime";

-- print invalid constraints
select
    -- `conrelid` is 0 if not a table constraint
    case
        when pg_constraint.conrelid != 0 then (pg_class.relname || '.')
        else ''
    end || pg_constraint.conname
from
    pg_constraint
    left outer join pg_class on pg_class.oid = pg_constraint.conrelid
where
    not convalidated;
