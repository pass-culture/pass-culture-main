--- espace dans le CP
UPDATE offerer SET "postalCode" = '75006' WHERE "postalCode" = '75006 ';  --- venue id 2979
UPDATE offerer SET "postalCode" = '67670' WHERE "postalCode" = '67670 ';  --- venue id 7223
UPDATE offerer SET "postalCode" = '77340' WHERE "postalCode" = '77340 ';  --- venue id 9473

--- typo dans le nom de la ville
UPDATE offerer SET "postalCode" = '49530', "city" = 'OREE D''ANJOU' WHERE "city" = 'OREE-D''ANJOU' AND "postalCode"='49270';  --- venue id 117190

--- CP CEDEX
UPDATE offerer SET "postalCode" = '93500' WHERE "postalCode" = '93507';  --- venue id 540
UPDATE offerer SET "city" = 'EVRY-COURCOURONNES' WHERE "city" = 'EVRY-CEDEX';  --- venue id 14815
UPDATE offerer SET "postalCode" = '59000', "city" = 'LILLE' WHERE "postalCode"='59040' AND "city" = 'LILLE CEDEX';  --- venue id 22310

--- regroupement de communes
UPDATE offerer SET "postalCode" = '93200', "city" = 'SAINT DENIS' WHERE "postalCode" = '93380' AND city = 'PIERREFITTE SUR SEINE';  --- venue id 703
UPDATE offerer SET "city" = 'PERN-LHOSPITALET' WHERE city = 'PERN';  --- venue id 60221

--- CP incorrect
UPDATE offerer SET "postalCode" = '75001' WHERE "postalCode" = '75000';  --- venue id 6525
