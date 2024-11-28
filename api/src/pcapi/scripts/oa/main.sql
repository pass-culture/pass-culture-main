BEGIN;

UPDATE venue SET "offererAddressId" = 97123 WHERE "offererAddressId" IN (94990, 95007, 34349);

UPDATE venue
SET
    "banId" = '09160_0350_00011',
    address = '11 Rue Jean Jaurès',
    city = 'Lavelanet',
    "postalCode" = '09300',
    latitude = '42.93',
    longitude = '1.85',
    "departementCode" = '09',
    timezone = 'Europe/Paris'
WHERE venue.id = 121454;

UPDATE offer SET "offererAddressId" = 97123 WHERE "offererAddressId" IN (94990, 95007, 34349);

COMMIT;