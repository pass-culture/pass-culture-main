import { IOfferEducationalFormValues } from 'core/OfferEducational'
import { hasStatusCode } from 'core/OfferEducational/utils'
import * as pcapi from 'repository/pcapi/pcapi'

import { createOfferPayload } from '../utils/createOfferPayload'

type Params = IOfferEducationalFormValues

interface IPayload {
  offerId: string | null
}

type PostOfferAdapter = Adapter<Params, IPayload>

const BAD_REQUEST_FAILING_RESPONSE = {
  isOk: false,
  message: 'Une ou plusieurs erreurs sont présentes dans le formulaire',
  payload: {
    offerId: null,
  },
}

const UNKNOWN_FAILING_RESPONSE = {
  isOk: false,
  message: 'Une erreur est survenue lors de la création de votre offre',
  payload: {
    offerId: null,
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
