import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'

type Params = {
  offerId: number
}

type PayloadSuccess = { id: string }
type PayloadFailure = null

type PostOfferAdapter = Adapter<Params, PayloadSuccess, PayloadFailure>

const BAD_REQUEST_FAILING_RESPONSE: AdapterFailure<PayloadFailure> = {
  isOk: false,
  message: 'Une ou plusieurs erreurs sont présentes dans le formulaire',
  payload: null,
}

const UNKNOWN_FAILING_RESPONSE: AdapterFailure<PayloadFailure> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la création de votre offre',
  payload: null,
}

const postCollectiveDuplicateOfferAdapter: PostOfferAdapter = async ({
  offerId,
}) => {
  try {
    const response = await api.duplicateCollectiveOffer(offerId)

    return {
      isOk: true,
      message: null,
      payload: {
        id: response.id,
      },
    }
  } catch (error) {
    if (isErrorAPIError(error) && error.status === 400) {
      return BAD_REQUEST_FAILING_RESPONSE
    }

    return UNKNOWN_FAILING_RESPONSE
  }
}

export default postCollectiveDuplicateOfferAdapter
