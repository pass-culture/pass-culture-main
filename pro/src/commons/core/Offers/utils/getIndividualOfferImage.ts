import type { GetIndividualOfferResponseModelV2 } from '@/apiClient/v1'
import type { IndividualOfferImage } from '@/commons/core/Offers/types'

export const getIndividualOfferImage = (
  offer: GetIndividualOfferResponseModelV2 | null
): IndividualOfferImage | undefined => {
  if (!offer) {
    return undefined
  }

  if (offer.activeMediation) {
    if (offer.activeMediation.thumbUrl) {
      return {
        url: offer.activeMediation.thumbUrl,
        credit: offer.activeMediation.credit || '',
      }
    }
  } else if (offer.thumbUrl) {
    // synchronized offers have thumbUrl but no mediation
    return {
      url: offer.thumbUrl,
      credit: '',
    }
  }

  return undefined
}
