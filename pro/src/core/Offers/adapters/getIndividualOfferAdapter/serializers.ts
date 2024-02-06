import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { IndividualOffer, IndividualOfferImage } from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'

export const serializeOfferApiExtraData = (
  apiOffer: GetIndividualOfferResponseModel
) => ({
  author: apiOffer.extraData?.author || '',
  gtl_id: apiOffer.extraData?.gtl_id || '',
  performer: apiOffer.extraData?.performer || '',
  ean: apiOffer.extraData?.ean || '',
  showType: apiOffer.extraData?.showType || '',
  showSubType: apiOffer.extraData?.showSubType || '',
  speaker: apiOffer.extraData?.speaker || '',
  stageDirector: apiOffer.extraData?.stageDirector || '',
  visa: apiOffer.extraData?.visa || '',
})

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
  const baseAccessibility = {
    [AccessiblityEnum.VISUAL]: apiOffer.visualDisabilityCompliant || false,
    [AccessiblityEnum.MENTAL]: apiOffer.mentalDisabilityCompliant || false,
    [AccessiblityEnum.AUDIO]: apiOffer.audioDisabilityCompliant || false,
    [AccessiblityEnum.MOTOR]: apiOffer.motorDisabilityCompliant || false,
  }

  const offer: IndividualOffer = {
    ...apiOffer,
    bookingEmail: apiOffer.bookingEmail || '',
    bookingContact: apiOffer.bookingContact || '',
    bookingsCount: apiOffer.bookingsCount || 0,
    description: apiOffer.description || '',
    durationMinutes: apiOffer.durationMinutes || null,
    url: apiOffer.url || '',
    externalTicketOfficeUrl: apiOffer.externalTicketOfficeUrl || '',
    withdrawalDetails: apiOffer.withdrawalDetails || '',
    withdrawalDelay:
      apiOffer.withdrawalDelay === undefined ? null : apiOffer.withdrawalDelay,
    withdrawalType: apiOffer.withdrawalType || null,
    image: serializeOfferApiImage(apiOffer),
    accessibility: {
      ...baseAccessibility,
      [AccessiblityEnum.NONE]: !Object.values(baseAccessibility).includes(true),
    },
    lastProviderName: apiOffer.lastProvider?.name || null,
    ...serializeOfferApiExtraData(apiOffer),
  }

  return offer
}
