import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { OFFER_STATUS_DRAFT, OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'

export const useOfferEditionURL = (
  isOfferEducational: boolean,
  offerId: number,
  isOfferFormV3: boolean,
  isShowcase?: boolean,
  status?: string
): string => {
  if (isOfferEducational) {
    const id = computeURLCollectiveOfferId(offerId, Boolean(isShowcase))
    return `/offre/${id}/collectif/recapitulatif`
  }
  if (status && status == OFFER_STATUS_DRAFT) {
    return getOfferIndividualUrl({
      offerId,
      mode: OFFER_WIZARD_MODE.DRAFT,
      step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
      isV2: !isOfferFormV3,
    })
  }

  return getOfferIndividualUrl({
    offerId,
    mode: OFFER_WIZARD_MODE.EDITION,
    step: OFFER_WIZARD_STEP_IDS.SUMMARY,
    isV2: !isOfferFormV3,
  })
}

export const useOfferStockEditionURL = (
  isOfferEducational: boolean,
  offerId: number,
  isOfferFormV3: boolean,
  isShowcase?: boolean
): string => {
  if (isOfferEducational) {
    const id = computeURLCollectiveOfferId(offerId, Boolean(isShowcase))
    return `/offre/${id}/collectif/stocks/edition`
  }

  return getOfferIndividualUrl({
    offerId,
    mode: OFFER_WIZARD_MODE.EDITION,
    step: OFFER_WIZARD_STEP_IDS.STOCKS,
    isV2: !isOfferFormV3,
  })
}
