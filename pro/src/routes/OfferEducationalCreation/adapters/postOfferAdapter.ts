import {
  IOfferEducationalFormValues,
  hasStatusCode,
} from 'core/OfferEducational'
import * as pcapi from 'repository/pcapi/pcapi'

import { createOfferPayload } from '../utils/createOfferPayload'

type Params = IOfferEducationalFormValues

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

const postOfferAdapter: PostOfferAdapter = async (
  offer: IOfferEducationalFormValues
) => {
  try {
    const payload = createOfferPayload(offer)

    const response = await pcapi.createEducationalOffer(payload)

    return {
      isOk: true,
      message: null,
      payload: {
        offerId: response.id,
        collectiveOfferId: response.collectiveOfferId,
      },
    }
  } catch (error) {
    if (hasStatusCode(error) && error.status === 400) {
      return BAD_REQUEST_FAILING_RESPONSE
    }

    return UNKNOWN_FAILING_RESPONSE
  }
}

export default postOfferAdapter
