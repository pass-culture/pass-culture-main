import useActiveFeature from './useActiveFeature'

const useOfferEditionURL = (
  isOfferEducational: boolean,
  offerId: string,
  isShowcase?: boolean
): string => {
  const enableIndividualAndCollectiveOfferSeparation = useActiveFeature(
    'ENABLE_INDIVIDUAL_AND_COLLECTIVE_OFFER_SEPARATION'
  )

  if (isOfferEducational) {
    const id =
      enableIndividualAndCollectiveOfferSeparation && isShowcase
        ? `T-${offerId}`
        : offerId
    return `/offre/${id}/collectif/edition`
  }

  return `/offre/${offerId}/individuel/edition`
}

export default useOfferEditionURL
