-- one label already exists for venue 36944:
update price_category set "priceCategoryLabelId" = 24823 where "priceCategoryLabelId" = 23936;
delete from price_category_label where id = 23936;

-- other labels do not already exist:
update price_category_label set "venueId" = 15497 where "venueId" = 36944;
