const useOfferEditionURL = (
  isOfferEducational: boolean,
  offerId: string
): string => {
  return isOfferEducational
    ? `/offre/${offerId}/collectif/edition`
    : `/offres/${offerId}/edition`
}

export default useOfferEditionURL
