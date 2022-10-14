import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm'

import { serializePatchOffer } from './serializers'

type TSuccessPayload = { id: string }
type TFailurePayload = { errors: Record<string, string> }
export type TUpdateIndividualOffer = Adapter<
  { offerId: string; formValues: IOfferIndividualFormValues },
  TSuccessPayload,
  TFailurePayload
>

const updateIndividualOffer: TUpdateIndividualOffer = async ({
  offerId,
  formValues,
}) => {
  /* istanbul ignore next: DEBT, TO FIX */
  try {
    const response = await api.patchOffer(
      offerId,
      serializePatchOffer(formValues)
    )
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
    const apiFieldsMap: Record<string, string> = {
      venue: 'venueId',
    }
    return {
      isOk: false,
      message: 'Une erreur est survenue lors de la création de votre offre',
      payload: {
        errors: serializeApiErrors(apiFieldsMap, formErrors),
      },
    }
  }
}

export default updateIndividualOffer
