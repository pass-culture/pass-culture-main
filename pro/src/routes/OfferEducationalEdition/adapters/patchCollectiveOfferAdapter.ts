import * as pcapi from 'repository/pcapi/pcapi'

import {
  CollectiveOffer,
  IOfferEducationalFormValues,
  hasStatusCode,
} from 'core/OfferEducational'

import { createPatchOfferPayload } from '../utils/createPatchOfferPayload'

type Params = {
  offerId: string
  offer: IOfferEducationalFormValues
  initialValues: IOfferEducationalFormValues
}

type PatchCollectiveOfferAdapter = Adapter<Params, CollectiveOffer, null>

const BAD_REQUEST_FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une ou plusieurs erreurs sont présentes dans le formulaire',
  payload: null,
}

const UNKNOWN_FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la modification de votre offre',
  payload: null,
}

const patchCollectiveOfferAdapter: PatchCollectiveOfferAdapter = async ({
  offerId,
  offer,
  initialValues,
}) => {
  try {
    const payload = createPatchOfferPayload(offer, initialValues, true)
    const updatedOffer = await pcapi.updateCollectiveOffer(offerId, payload)
    const isBooked = updatedOffer.collectiveStock.isBooked

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

export default patchCollectiveOfferAdapter
