import type { CollectiveOfferResponseModel } from '@/apiClient/adage'
import { formatPrice } from '@/commons/utils/formatPrice'

export function getBookableOfferStockPrice(
  offer: CollectiveOfferResponseModel
) {
  const formattedPrice = formatPrice(offer.stock.price / 100, {
    minimumFractionDigits: 0,
  })

  const totalParticipants =
    (offer.stock.numberOfTickets ?? 0) + (offer.stock.numberOfTeachers ?? 0)

  return `${formattedPrice} pour ${totalParticipants} participants`
}
