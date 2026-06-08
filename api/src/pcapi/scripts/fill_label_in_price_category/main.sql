UPDATE price_category
SET label = price_category_label.label
FROM price_category_label
WHERE price_category_label.id = price_category."priceCategoryLabelId"
AND price_category.label IS NULL;
