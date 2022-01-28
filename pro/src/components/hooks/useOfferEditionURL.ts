const useOfferEditionURL = (
  isOfferEducational: boolean,
  offerId: string
): string => {
  return isOfferEducational
    ? `/offre/${offerId}/scolaire/edition`
    : `/offres/${offerId}/edition`
}

export default useOfferEditionURL
