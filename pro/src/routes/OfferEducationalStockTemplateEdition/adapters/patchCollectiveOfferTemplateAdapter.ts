import * as pcapi from 'repository/pcapi/pcapi'

import {
  GetStockOfferSuccessPayload,
  OfferEducationalStockFormValues,
  StockResponse,
  hasStatusCode,
} from 'core/OfferEducational'

export type Params = {
  offer: GetStockOfferSuccessPayload
  values: OfferEducationalStockFormValues
}

type patchCollectiveOfferTemplateAdapter = Adapter<Params, StockResponse, null>

const BAD_REQUEST_FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une ou plusieurs erreurs sont présentes dans le formulaire',
  payload: null,
}

const UNKNOWN_FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la mise à jour de votre stock.',
  payload: null,
}

export const patchCollectiveOfferTemplateAdapter: patchCollectiveOfferTemplateAdapter =
  async ({ offer, values }) => {
    try {
      // the api returns no understandable error when the id is not valid, so we deal before calling the api
      if (!offer.id || offer.id === '') {
        throw new Error('L’identifiant de l’offre n’est pas valide.')
      }

      const updatedOffer = await pcapi.patchCollectiveOfferTemplate(offer.id, {
        priceDetail: values.priceDetail,
      })

      return {
        isOk: true,
        message: 'Votre stock a bien été modifiée.',
        payload: updatedOffer,
      }
    } catch (error) {
      if (hasStatusCode(error) && error.status === 400) {
        return BAD_REQUEST_FAILING_RESPONSE
      } else {
        return {
          ...UNKNOWN_FAILING_RESPONSE,
          message: `${UNKNOWN_FAILING_RESPONSE.message} ${
            // @ts-expect-error property message does not exist on error
            error?.message ? `${error?.message}` : ''
          }`,
        }
      }
    }
  }
