import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { OFFER_STATUS_DRAFT, OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'

export const useOfferEditionURL = (
  isOfferEducational: boolean,
  offerId: number,
  isShowcase?: boolean,
  status?: string
): string => {
  if (isOfferEducational) {
    const id = computeURLCollectiveOfferId(offerId, Boolean(isShowcase))
    return `/offre/${id}/collectif/recapitulatif`
  }
  if (status && status == OFFER_STATUS_DRAFT) {
    return getIndividualOfferUrl({
      offerId,
      mode: OFFER_WIZARD_MODE.DRAFT,
      step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
    })
  }

  return getIndividualOfferUrl({
    offerId,
    mode: OFFER_WIZARD_MODE.EDITION,
    step: OFFER_WIZARD_STEP_IDS.SUMMARY,
  })
}

export const useOfferStockEditionURL = (
  isOfferEducational: boolean,
  offerId: number,
  isShowcase?: boolean
): string => {
  if (isOfferEducational) {
    const id = computeURLCollectiveOfferId(offerId, Boolean(isShowcase))
    return `/offre/${id}/collectif/stocks/edition`
  }

  return getIndividualOfferUrl({
    offerId,
    mode: OFFER_WIZARD_MODE.EDITION,
    step: OFFER_WIZARD_STEP_IDS.STOCKS,
  })
}
