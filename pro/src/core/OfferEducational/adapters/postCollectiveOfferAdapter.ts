import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { IOfferEducationalFormValues } from 'core/OfferEducational'

import { createCollectiveOfferPayload } from '../utils/createOfferPayload'

type Params = {
  offer: IOfferEducationalFormValues
  offerTemplateId?: string
}

type IPayloadSuccess = { id: string }
type IPayloadFailure = { id: null }

type PostOfferAdapter = Adapter<Params, IPayloadSuccess, IPayloadFailure>

const BAD_REQUEST_FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message: 'Une ou plusieurs erreurs sont présentes dans le formulaire',
  payload: {
    id: null,
  },
}

const UNKNOWN_FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
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

export default postCollectiveOfferAdapter
