import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { IndividualOffer, IndividualOfferImage } from 'core/Offers/types'

export const serializeOfferApiImage = (
  apiOffer: GetIndividualOfferResponseModel
): IndividualOfferImage | undefined => {
  if (apiOffer.activeMediation) {
    if (apiOffer.activeMediation.thumbUrl) {
      return {
        originalUrl: apiOffer.activeMediation.thumbUrl,
        url: apiOffer.activeMediation.thumbUrl,
        credit: apiOffer.activeMediation?.credit || '',
      }
    }
  } else if (apiOffer.thumbUrl) {
    // synchronized offers have thumbUrl but no mediation
    return {
      originalUrl: apiOffer.thumbUrl,
      url: apiOffer.thumbUrl,
      credit: '',
    }
  }
  return undefined
}

export const serializeOfferApi = (
  apiOffer: GetIndividualOfferResponseModel
): IndividualOffer => {
  const offer: IndividualOffer = {
    ...apiOffer,
    image: serializeOfferApiImage(apiOffer),
  }

  return offer
}
