import type { CollectiveOfferResponseModel } from '@/apiClient/adage'

export function getBookableOfferStockPrice(
  offer: CollectiveOfferResponseModel,
  isNewCollectivePriceEnabled = false
) {
  const formattedPrice = Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
  }).format(offer.stock.price / 100)

  if (isNewCollectivePriceEnabled) {
    const totalParticipants =
      (offer.stock.numberOfTickets ?? 0) + (offer.stock.numberOfTeachers ?? 0)
    return `${formattedPrice} pour ${totalParticipants} participants`
  }

  return `${formattedPrice} pour ${offer.stock.numberOfTickets} participants`
}
