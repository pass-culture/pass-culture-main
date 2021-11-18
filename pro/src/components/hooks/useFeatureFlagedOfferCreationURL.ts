import useActiveFeature from 'components/hooks/useActiveFeature'

/* TODO : delete this file and all hooks instances when FF is done */

const useFeatureFlagedOfferCreationURL = ():
  | '/offres/creation'
  | '/offre/creation' => {
  return useActiveFeature('ENABLE_NEW_EDUCATIONAL_OFFER_CREATION_FORM')
    ? '/offre/creation'
    : '/offres/creation'
}

export default useFeatureFlagedOfferCreationURL
