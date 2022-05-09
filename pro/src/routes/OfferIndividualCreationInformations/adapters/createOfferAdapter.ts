import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm'

const createOfferAdapter = async (
  formValues: IOfferIndividualFormValues
): Promise<string | void> => {
  console.log('createOfferAdapter::called with', formValues)

  // TODO (rlecellier): replace this fake offer id by api response id
  return 'AL4Q'
}

export default createOfferAdapter
