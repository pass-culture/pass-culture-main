import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { IOfferEducationalFormValues } from 'core/OfferEducational'

import { createCollectiveOfferPayload } from '../utils/createOfferPayload'

type Params = {
  offer: IOfferEducationalFormValues
}

type IPayloadSuccess = { offerId: string }
type IPayloadFailure = { offerId: null }

type PostOfferAdapter = Adapter<Params, IPayloadSuccess, IPayloadFailure>

const BAD_REQUEST_FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message: 'Une ou plusieurs erreurs sont présentes dans le formulaire',
  payload: {
    offerId: null,
  },
}

const UNKNOWN_FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la création de votre offre',
  payload: {
    offerId: null,
  },
}

const postCollectiveOfferTemplateAdapter: PostOfferAdapter = async ({
  offer,
}) => {
  try {
    const payload = createCollectiveOfferPayload(offer, true)

    const response = await api.createCollectiveOfferTemplate(payload)

    return {
      isOk: true,
      message: null,
      payload: {
        offerId: response.id,
      },
    }
  } catch (error) {
    if (isErrorAPIError(error) && error.status === 400) {
      return BAD_REQUEST_FAILING_RESPONSE
    }

    return UNKNOWN_FAILING_RESPONSE
  }
}

export default postCollectiveOfferTemplateAdapter
