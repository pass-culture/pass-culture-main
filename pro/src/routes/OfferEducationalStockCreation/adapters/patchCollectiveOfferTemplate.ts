import {
  hasStatusCode,
  hasStatusCodeAndErrorsCode,
  IOfferEducationalFormValues,
} from 'core/OfferEducational'
import { Offer } from 'custom_types/offer'
import * as pcapi from 'repository/pcapi/pcapi'
import { createPatchOfferPayload } from 'routes/OfferEducationalEdition/utils/createPatchOfferPayload'

type Params = {
  offerId: string
  offer: IOfferEducationalFormValues
  initialValues: IOfferEducationalFormValues
}

type PatchCollectiveOfferTemplateAdapter = Adapter<Params, Offer, null>

const KNOWN_BAD_REQUEST_CODES: Record<string, string> = {
  INVALID_SUBCATEGORY_FOR_COLLECTIVE_OFFER:
    "Cette catégorie n'est pas valide pour les offres collectives.",
  COLLECTIVE_OFFER_NOT_FOUND:
    "Une erreur s'est produite. L'offre n'a pas été trouvée.",
}

const BAD_REQUEST_FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une ou plusieurs erreurs sont présentes dans le formulaire',
  payload: null,
}

const UNKNOWN_FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la création de votre stock.',
  payload: null,
}

const patchCollectiveOfferTemplateAdapter: PatchCollectiveOfferTemplateAdapter =
  async ({ offerId, offer, initialValues }: Params) => {
    try {
      const payload = createPatchOfferPayload(offer, initialValues)
      const updatedOffer = (await pcapi.patchCollectiveOfferTemplate(
        offerId,
        payload
      )) as Offer
      return {
        isOk: true,
        message: 'Votre offre a bien été modifiée.',
        payload: { ...updatedOffer, isBooked: false },
      }
    } catch (error) {
      if (hasStatusCodeAndErrorsCode(error) && error.status === 400) {
        if (error.errors.code in KNOWN_BAD_REQUEST_CODES) {
          return {
            ...BAD_REQUEST_FAILING_RESPONSE,
            message: KNOWN_BAD_REQUEST_CODES[error.errors.code],
          }
        }
      }
      if (hasStatusCode(error) && error.status === 400) {
        return BAD_REQUEST_FAILING_RESPONSE
      } else {
        return UNKNOWN_FAILING_RESPONSE
      }
    }
  }

export default patchCollectiveOfferTemplateAdapter
