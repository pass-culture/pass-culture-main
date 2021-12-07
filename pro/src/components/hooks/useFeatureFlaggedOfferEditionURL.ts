import useActiveFeature from 'components/hooks/useActiveFeature'

/* TODO : delete this file and all hooks instances when FF is done */

const useFeatureFlagedOfferEditionURL = (
  isOfferEducational: boolean,
  offerId: string
): string => {
  const isFeatureActive = useActiveFeature(
    'ENABLE_NEW_EDUCATIONAL_OFFER_CREATION_FORM'
  )

  return isOfferEducational && isFeatureActive
    ? `/offre/${offerId}/scolaire/edition`
    : `/offres/${offerId}/edition`
}

export default useFeatureFlagedOfferEditionURL
