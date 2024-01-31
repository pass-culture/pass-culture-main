/* istanbul ignore file: DEBT, TO FIX */

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { IndividualOfferFormValues } from 'components/IndividualOfferForm'

import { serializePostOffer } from './serializers'

type SuccessPayload = { id: number }
type FailurePayload = { errors: Record<string, string> }
type GetCategorySuggestion = Adapter<
  IndividualOfferFormValues,
  SuccessPayload,
  FailurePayload
>

const getCategorySuggestion: GetCategorySuggestion = async (formValues) => {
  try {
    const response = await api.getCategorySuggestion()
    return {
      isOk: true,
      message: '',
      payload: {
        id: response.id,
      },
    }
  } catch (error) {
    let formErrors = {}
    /* istanbul ignore next: DEBT, TO FIX */
    if (isErrorAPIError(error)) {
      formErrors = error.body
    }
    const apiFieldsMap: Record<string, string> = {
      venue: 'venueId',
    }
    return {
      isOk: false,
      message: 'Une erreur est survenue lors de la création de votre offre',
      payload: {
        errors: serializeApiErrors(formErrors, apiFieldsMap),
      },
    }
  }
}

export default createIndividualOffer
