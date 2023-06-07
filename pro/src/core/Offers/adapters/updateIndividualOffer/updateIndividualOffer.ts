import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { PatchOfferBodyModel } from 'apiClient/v1'

type TSuccessPayload = { nonHumanizedId: number }
type TFailurePayload = { errors: Record<string, string> }
type TUpdateIndividualOffer = Adapter<
  { serializedOffer: PatchOfferBodyModel; offerId: number },
  TSuccessPayload,
  TFailurePayload
>

const updateIndividualOffer: TUpdateIndividualOffer = async ({
  serializedOffer,
  offerId,
}) => {
  /* istanbul ignore next: DEBT, TO FIX */
  try {
    const response = await api.patchOffer(offerId, serializedOffer)
    return {
      isOk: true,
      message: '',
      payload: {
        nonHumanizedId: response.nonHumanizedId,
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
        errors: serializeApiErrors(formErrors, apiFieldsMap),
      },
    }
  }
}

export default updateIndividualOffer
