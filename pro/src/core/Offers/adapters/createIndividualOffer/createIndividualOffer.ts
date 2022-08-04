import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm'

import { serializeApiErrors, serializePostOffer } from './serializers'

type TSuccessPayload = { id: string }
type TFailurePayload = { errors: Record<string, string> }
export type TCreateIndividualOffer = Adapter<
  IOfferIndividualFormValues,
  TSuccessPayload,
  TFailurePayload
>

const createIndividualOffer: TCreateIndividualOffer = async formValues => {
  try {
    const response = await api.postOffer(serializePostOffer(formValues))
    return {
      isOk: true,
      message: '',
      payload: {
        id: response.id,
      },
    }
  } catch (error) {
    let formErrors = {}
    if (isErrorAPIError(error)) {
      formErrors = error.body
    }
    return {
      isOk: false,
      message: 'Une erreur est survenue lors de la création de votre offre',
      payload: {
        errors: serializeApiErrors(formErrors),
      },
    }
  }
}

export default createIndividualOffer
