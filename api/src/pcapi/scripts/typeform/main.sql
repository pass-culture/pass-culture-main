-- Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
-- Assumed path to the script (copy-paste in github actions):
-- https://github.com/pass-culture/pass-culture-main/blob/pc-36356-rpa-close-old-typeforms/api/src/pcapi/scripts/typeform/main.py


UPDATE
	special_event
SET
	"endImportDate" = NOW()
WHERE
	"dateCreated" < '2025-05-28'::date
	AND "endImportDate" > NOW();