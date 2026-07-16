BEGIN;
-- remove email adresse from website field
update venue_contact set website=null where website is not null and lower(website) not like 'http%' and website like '%@%' and id != 34312;

-- add url scheme to websites url
update venue_contact set website=concat('https://', website) where website is not null and lower(website) not like 'http%';

COMMIT;