import useActiveFeature from './useActiveFeature'

const getOfferId = (
  offerId: string,
  enableIndividualAndCollectiveOfferSeparation: boolean,
  isShowcase?: boolean
) =>
  enableIndividualAndCollectiveOfferSeparation && isShowcase
    ? `T-${offerId}`
    : offerId

export const useOfferEditionURL = (
  isOfferEducational: boolean,
  offerId: string,
  isShowcase?: boolean
): string => {
  const enableIndividualAndCollectiveOfferSeparation = useActiveFeature(
    'ENABLE_INDIVIDUAL_AND_COLLECTIVE_OFFER_SEPARATION'
  )

  if (isOfferEducational) {
    const id = getOfferId(
      offerId,
      enableIndividualAndCollectiveOfferSeparation,
      isShowcase
    )
    return `/offre/${id}/collectif/edition`
  }

  return `/offre/${offerId}/individuel/edition`
}

export const useOfferStockEditionURL = (
  isOfferEducational: boolean,
  offerId: string,
  isShowcase?: boolean
): string => {
  const enableIndividualAndCollectiveOfferSeparation = useActiveFeature(
    'ENABLE_INDIVIDUAL_AND_COLLECTIVE_OFFER_SEPARATION'
  )

  if (isOfferEducational) {
    const id = getOfferId(
      offerId,
      enableIndividualAndCollectiveOfferSeparation,
      isShowcase
    )
    return `/offre/${id}/collectif/stocks/edition`
  }

  return `/offre/${offerId}/individuel/stocks`
}
