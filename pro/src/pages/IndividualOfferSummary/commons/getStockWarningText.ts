import {
  type GetIndividualOfferResponseModelV2,
  OfferStatus,
} from '@/apiClient/v1'

export const getStockWarningText = (
  offer: GetIndividualOfferResponseModelV2
) => {
  if (!offer.hasStocks) {
    return 'Vous n’avez aucun stock renseigné.'
  }

  if (offer.status === OfferStatus.SOLD_OUT) {
    return 'Votre stock est épuisé.'
  }

  if (offer.status === OfferStatus.EXPIRED) {
    return 'Votre stock est expiré.'
  }

  return false
}
