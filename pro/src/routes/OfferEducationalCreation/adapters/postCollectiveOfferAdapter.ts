import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { IOfferEducationalFormValues } from 'core/OfferEducational'

import { createCollectiveOfferPayload } from '../utils/createOfferPayload'

type Params = {
  offer: IOfferEducationalFormValues
}

type IPayloadSuccess = { offerId: string; collectiveOfferId: string }
type IPayloadFailure = { offerId: null; collectiveOfferId: null }

type PostOfferAdapter = Adapter<Params, IPayloadSuccess, IPayloadFailure>

const BAD_REQUEST_FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message: 'Une ou plusieurs erreurs sont présentes dans le formulaire',
  payload: {
    offerId: null,
    collectiveOfferId: null,
  },
}

const UNKNOWN_FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la création de votre offre',
  payload: {
    offerId: null,
    collectiveOfferId: null,
  },
}

const postCollectiveOfferAdapter: PostOfferAdapter = async ({ offer }) => {
  try {
    const payload = createCollectiveOfferPayload(offer)

    const response = await api.createCollectiveOffer(payload)

    return {
      isOk: true,
      message: null,
      payload: {
        offerId: response.id,
        collectiveOfferId: response.id,
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
