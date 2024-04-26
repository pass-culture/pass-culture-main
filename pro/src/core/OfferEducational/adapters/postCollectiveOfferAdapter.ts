import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'

import { OfferEducationalFormValues } from '../types'
import { createCollectiveOfferPayload } from '../utils/createOfferPayload'

type Params = {
  offer: OfferEducationalFormValues
  offerTemplateId?: number
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

export const postCollectiveOfferAdapter: PostOfferAdapter = async ({
  offer,
  offerTemplateId,
}) => {
  try {
    const payload = createCollectiveOfferPayload(offer, offerTemplateId)

    const response = await api.createCollectiveOffer(payload)

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
