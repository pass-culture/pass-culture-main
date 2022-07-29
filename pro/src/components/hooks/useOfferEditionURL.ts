const getOfferId = (offerId: string, isShowcase?: boolean) =>
  isShowcase ? `T-${offerId}` : offerId

export const useOfferEditionURL = (
  isOfferEducational: boolean,
  offerId: string,
  isOfferFormV3: boolean,
  isShowcase?: boolean
): string => {
  if (isOfferEducational) {
    const id = getOfferId(offerId, isShowcase)
    return `/offre/${id}/collectif/edition`
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
    const id = getOfferId(offerId, isShowcase)
    return `/offre/${id}/collectif/stocks/edition`
  }

  return `/offre/${offerId}/individuel/stocks`
}
