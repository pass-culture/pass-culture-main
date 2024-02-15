import { CollectiveOfferResponseModel } from 'apiClient/adage'

export function getBookableOfferStockPrice(
  offer: CollectiveOfferResponseModel
) {
  return `${Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
  }).format(offer.stock.price)} pour ${offer.stock.numberOfTickets} élèves`
}
