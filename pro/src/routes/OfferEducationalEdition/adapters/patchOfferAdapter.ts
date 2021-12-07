import { IOfferEducationalFormValues } from 'core/OfferEducational'
import { hasStatusCode } from 'core/OfferEducational/utils'
import * as pcapi from 'repository/pcapi/pcapi'

import { createPatchOfferPayload } from '../utils/createPatchOfferPayload'

type Params = {
  offerId: string
  offer: IOfferEducationalFormValues
  initialValues: IOfferEducationalFormValues
}

type PostOfferAdapter = Adapter<Params, null>

const BAD_REQUEST_FAILING_RESPONSE = {
  isOk: false,
  message: 'Une ou plusieurs erreurs sont présentes dans le formulaire',
  payload: null,
}

const UNKNOWN_FAILING_RESPONSE = {
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
    await pcapi.updateEducationalOffer(offerId, payload)

    return {
      isOk: true,
      message: 'Votre offre a bien été modifiée.',
      payload: null,
    }
  } catch (error) {
    if (hasStatusCode(error) && error.status === 400) {
      return BAD_REQUEST_FAILING_RESPONSE
    }

    return UNKNOWN_FAILING_RESPONSE
  }
}

export default patchOfferAdapter
