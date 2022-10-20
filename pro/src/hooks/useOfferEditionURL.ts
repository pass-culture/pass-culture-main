import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { OFFER_STATUS_DRAFT } from 'core/Offers'

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
    return `/offre/${offerId}/individuel/brouillon`

  return isOfferFormV3
    ? `/offre/${offerId}/v3/individuelle/recapitulatif`
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
    ? `/offre/${offerId}/v3/individuelle/stocks`
    : `/offre/${offerId}/individuel/stocks`
}
