const useOfferStockEditionURL = (
  isOfferEducational: boolean,
  offerId: string
): string => {
  return isOfferEducational
    ? `/offre/${offerId}/collectif/stocks/edition`
    : `/offre/${offerId}/individuel/stocks`
}

export default useOfferStockEditionURL
