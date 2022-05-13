import * as pcapi from 'repository/pcapi/pcapi'

import {
  IOfferEducationalFormValues,
  hasStatusCode,
} from 'core/OfferEducational'

import { Offer } from 'custom_types/offer'
import { createPatchOfferPayload } from '../utils/createPatchOfferPayload'

type Params = {
  offerId: string
  offer: IOfferEducationalFormValues
  initialValues: IOfferEducationalFormValues
}

type PostOfferAdapter = Adapter<Params, Offer, null>

const BAD_REQUEST_FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une ou plusieurs erreurs sont présentes dans le formulaire',
  payload: null,
}

const UNKNOWN_FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la création de votre offre',
  payload: null,
}

const patchOfferAdapter: PostOfferAdapter = async ({
  offerId,
  offer,
  initialValues,
}) => {
  try {
    const payload = createPatchOfferPayload(offer, initialValues)
    const updatedOffer = await pcapi.updateEducationalOffer(offerId, payload)
    const isBooked = updatedOffer.stocks[0]?.bookingsQuantity > 0

    return {
      isOk: true,
      message: 'Votre offre a bien été modifiée.',
      payload: { ...updatedOffer, isBooked },
    }
  } catch (error) {
    if (hasStatusCode(error) && error.status === 400) {
      return BAD_REQUEST_FAILING_RESPONSE
    }

    return UNKNOWN_FAILING_RESPONSE
  }
}

export default patchOfferAdapter
