import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { OfferEducationalFormValues } from 'core/OfferEducational'

import { createCollectiveOfferPayload } from '../utils/createOfferPayload'

type Params = {
  offer: OfferEducationalFormValues
  offerTemplateId?: number
}

type PayloadSuccess = { nonHumanizedId: number }
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

const postCollectiveOfferAdapter: PostOfferAdapter = async ({
  offer,
  offerTemplateId,
}) => {
  try {
    const payload = createCollectiveOfferPayload(offer, false, offerTemplateId)

    const response = await api.createCollectiveOffer(payload)

    return {
      isOk: true,
      message: null,
      payload: {
        nonHumanizedId: response.nonHumanizedId,
      },
    }
  } catch (error) {
    if (isErrorAPIError(error) && error.status === 400) {
      return BAD_REQUEST_FAILING_RESPONSE
    }

    return UNKNOWN_FAILING_RESPONSE
  }
}

export default postCollectiveOfferAdapter
