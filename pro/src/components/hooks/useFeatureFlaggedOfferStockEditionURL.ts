import useActiveFeature from 'components/hooks/useActiveFeature'

/* TODO : delete this file and all hooks instances when FF is done */

const useFeatureFlagedOfferStockEditionURL = (
  isOfferEducational: boolean,
  offerId: string
): string => {
  const isFeatureActive = useActiveFeature(
    'ENABLE_NEW_EDUCATIONAL_OFFER_CREATION_FORM'
  )

  return isOfferEducational && isFeatureActive
    ? `/offre/${offerId}/scolaire/stocks/edition`
    : `/offres/${offerId}/stocks`
}

export default useFeatureFlagedOfferStockEditionURL
