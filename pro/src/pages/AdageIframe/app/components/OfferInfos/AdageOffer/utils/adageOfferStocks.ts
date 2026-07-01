import type { CollectiveOfferResponseModel } from '@/apiClient/adage'
import { formatPrice } from '@/commons/utils/formatPrice'

export function getBookableOfferStockPrice(
  offer: CollectiveOfferResponseModel,
  isNewCollectivePriceEnabled = false
) {
  const formattedPrice = formatPrice(offer.stock.price / 100, {
    minimumFractionDigits: 0,
  })

  if (isNewCollectivePriceEnabled) {
    const totalParticipants =
      (offer.stock.numberOfTickets ?? 0) + (offer.stock.numberOfTeachers ?? 0)
    return `${formattedPrice} pour ${totalParticipants} participants`
  }

  return `${formattedPrice} pour ${offer.stock.numberOfTickets} participants`
}
