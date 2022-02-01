const useOfferEditionURL = (
  isOfferEducational: boolean,
  offerId: string
): string => {
  return isOfferEducational
    ? `/offre/${offerId}/collectif/edition`
    : `/offre/${offerId}/individuel/edition`
}

export default useOfferEditionURL
