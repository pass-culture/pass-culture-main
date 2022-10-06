import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'

export const useOfferEditionURL = (
  isOfferEducational: boolean,
  offerId: string,
  isOfferFormV3: boolean,
  isShowcase?: boolean
): string => {
  if (isOfferEducational) {
    const id = computeURLCollectiveOfferId(offerId, Boolean(isShowcase))
    return `/offre/${id}/collectif/recapitulatif`
  }

  return isOfferFormV3
    ? `/offre/${offerId}/v3/individuelle/recapitulatif`
    : `/offre/${offerId}/individuel/recapitulatif`
}

export const useOfferStockEditionURL = (
  isOfferEducational: boolean,
  offerId: string,
  isShowcase?: boolean
): string => {
  if (isOfferEducational) {
    const id = computeURLCollectiveOfferId(offerId, Boolean(isShowcase))
    return `/offre/${id}/collectif/stocks/edition`
  }

  return `/offre/${offerId}/individuel/stocks`
}
