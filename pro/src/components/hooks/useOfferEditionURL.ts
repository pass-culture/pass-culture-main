const getOfferId = (offerId: string, isShowcase?: boolean) =>
  isShowcase ? `T-${offerId}` : offerId

export const useOfferEditionURL = (
  isOfferEducational: boolean,
  offerId: string,
  useSummaryPage: boolean,
  isShowcase?: boolean
): string => {
  if (isOfferEducational) {
    const id = getOfferId(offerId, isShowcase)
    return `/offre/${id}/collectif/edition`
  }

  return useSummaryPage
    ? `/offre/${offerId}/individuel/recapitulatif`
    : `/offre/${offerId}/individuel/edition`
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
