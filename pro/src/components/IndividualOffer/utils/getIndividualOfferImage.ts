import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { IndividualOfferImage } from 'commons/core/Offers/types'

export const getIndividualOfferImage = (
  offer: GetIndividualOfferResponseModel | null
): IndividualOfferImage | undefined => {
  if (!offer) {
    return undefined
  }

  if (offer.activeMediation) {
    if (offer.activeMediation.thumbUrl) {
      return {
        originalUrl: offer.activeMediation.thumbUrl,
        url: offer.activeMediation.thumbUrl,
        credit: offer.activeMediation.credit || '',
      }
    }
  } else if (offer.thumbUrl) {
    // synchronized offers have thumbUrl but no mediation
    return {
      originalUrl: offer.thumbUrl,
      url: offer.thumbUrl,
      credit: '',
    }
  }

  return undefined
}
