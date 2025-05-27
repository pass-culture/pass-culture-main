UPDATE product
SET "gcuCompatibilityType" = 'WHITELISTED'
WHERE ean IN (SELECT ean FROM product_whitelist);