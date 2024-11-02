select
    offer.id as offerId,
    offer.name as offerName,
    offer."lastProviderId" as offerProvider,
    provider.name as offerProviderName,
    offer."jsonData" -> 'ean' as offerEan,
    offer."jsonData" -> 'allocineId' as offerAllocineId,
    product.id as productId,
    product."jsonData" -> 'ean' as productEan,
    product."jsonData" -> 'allocineId' as productAllocineId,
    product.last_30_days_booking,
    product."lastProviderId" as productProvider,
    offer."subcategoryId",
    product."subcategoryId"
from
    offer
    left outer join product on offer."productId" = product.id
    left outer join provider on offer."lastProviderId" = provider.id
where
    offer.id = 245960929;