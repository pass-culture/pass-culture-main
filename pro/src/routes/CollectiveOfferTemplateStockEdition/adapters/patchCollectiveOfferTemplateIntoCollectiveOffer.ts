import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { CollectiveOfferFromTemplateResponseModel } from 'apiClient/v1'
import {
  OfferEducationalStockFormValues,
  createStockDataPayload,
} from 'core/OfferEducational'

export type Params = {
  offerId: string
  departmentCode: string
  values: OfferEducationalStockFormValues
}

type patchCollectiveOfferTemplateIntoCollectiveOfferAdapter = Adapter<
  Params,
  CollectiveOfferFromTemplateResponseModel,
  null
>

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

export const patchCollectiveOfferTemplateIntoCollectiveOfferAdapter: patchCollectiveOfferTemplateIntoCollectiveOfferAdapter =
  async ({ offerId, departmentCode, values }) => {
    try {
      // the api returns no understandable error when the id is not valid, so we deal before calling the api
      if (!offerId || offerId === '')
        throw new Error('L’identifiant de l’offre n’est pas valide.')
      const payload = createStockDataPayload(values, departmentCode, offerId)
      const updatedOffer =
        await api.transformCollectiveOfferTemplateIntoCollectiveOffer(
          offerId,
          payload
        )

      return {
        isOk: true,
        message: 'Votre stock a bien été modifiée.',
        payload: updatedOffer,
      }
    } catch (error) {
      if (isErrorAPIError(error) && error.status === 400) {
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
