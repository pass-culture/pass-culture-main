import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm'

const createOfferAdapter = async (
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  formValues: IOfferIndividualFormValues
): Promise<string | void> => {
  // TODO (rlecellier): replace this fake offer id by api response id
  return 'AL4Q'
}

export default createOfferAdapter
