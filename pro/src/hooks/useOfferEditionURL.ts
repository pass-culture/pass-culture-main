import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { OFFER_STATUS_DRAFT, OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'

export const useOfferEditionURL = (
  isOfferEducational: boolean,
  offerId: string,
  isOfferFormV3: boolean,
  isShowcase?: boolean,
  status?: string
): string => {
  if (isOfferEducational) {
    const id = computeURLCollectiveOfferId(offerId, Boolean(isShowcase))
    return `/offre/${id}/collectif/recapitulatif`
  }
  if (status && status == OFFER_STATUS_DRAFT)
    return isOfferFormV3
      ? getOfferIndividualUrl({
          offerId,
          mode: OFFER_WIZARD_MODE.DRAFT,
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        })
      : `/offre/${offerId}/individuel/brouillon`

  return isOfferFormV3
    ? getOfferIndividualUrl({
        offerId,
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.SUMMARY,
      })
    : `/offre/${offerId}/individuel/recapitulatif`
}

export const useOfferStockEditionURL = (
  isOfferEducational: boolean,
  offerId: string,
  isOfferFormV3: boolean,
  isShowcase?: boolean
): string => {
  if (isOfferEducational) {
    const id = computeURLCollectiveOfferId(offerId, Boolean(isShowcase))
    return `/offre/${id}/collectif/stocks/edition`
  }

  return isOfferFormV3
    ? getOfferIndividualUrl({
        offerId,
        mode: OFFER_WIZARD_MODE.EDITION,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
      })
    : `/offre/${offerId}/individuel/stocks`
}
