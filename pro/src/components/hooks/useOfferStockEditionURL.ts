const useOfferStockEditionURL = (
  isOfferEducational: boolean,
  offerId: string
): string => {
  return isOfferEducational
    ? `/offre/${offerId}/scolaire/stocks/edition`
    : `/offres/${offerId}/stocks`
}

export default useOfferStockEditionURL
