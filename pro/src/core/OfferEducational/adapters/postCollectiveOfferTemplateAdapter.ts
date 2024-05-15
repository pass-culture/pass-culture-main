import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'

import { OfferEducationalFormValues } from '../types'
import { createCollectiveOfferTemplatePayload } from '../utils/createOfferPayload'

type Params = {
  offer: OfferEducationalFormValues
  isCustomContactActive: boolean
}

type PayloadSuccess = { id: number }
type PayloadFailure = { id: null }

type PostOfferAdapter = Adapter<Params, PayloadSuccess, PayloadFailure>

const BAD_REQUEST_FAILING_RESPONSE: AdapterFailure<PayloadFailure> = {
  isOk: false,
  message: 'Une ou plusieurs erreurs sont présentes dans le formulaire',
  payload: {
    id: null,
  },
}

const UNKNOWN_FAILING_RESPONSE: AdapterFailure<PayloadFailure> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la création de votre offre',
  payload: {
    id: null,
  },
}

export const postCollectiveOfferTemplateAdapter: PostOfferAdapter = async ({
  offer,
  isCustomContactActive,
}) => {
  try {
    const payload = createCollectiveOfferTemplatePayload(
      offer,
      isCustomContactActive
    )

    const response = await api.createCollectiveOfferTemplate(payload)

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
