import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import {
  CollectiveOffer,
  IOfferEducationalFormValues,
} from 'core/OfferEducational'

import { createPatchOfferPayload } from '../../../pages/CollectiveOfferEdition/utils/createPatchOfferPayload'

type Params = {
  offerId: number
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
    const payload = createPatchOfferPayload(offer, initialValues, false)
    const updatedOffer = await api.editCollectiveOffer(offerId, payload)

    return {
      isOk: true,
      message: 'Votre offre a bien été modifiée.',
      payload: { ...updatedOffer, isTemplate: false },
    }
  } catch (error) {
    if (isErrorAPIError(error) && error.status === 400) {
      return BAD_REQUEST_FAILING_RESPONSE
    }

    return UNKNOWN_FAILING_RESPONSE
  }
}

export default patchCollectiveOfferAdapter
