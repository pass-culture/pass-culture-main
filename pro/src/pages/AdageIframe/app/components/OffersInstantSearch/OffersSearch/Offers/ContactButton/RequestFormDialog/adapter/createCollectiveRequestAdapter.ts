import { apiAdage } from 'apiClient/api'

import { RequestFormValues } from '../type'

import { createCollectiveRequestPayload } from './createCollectiveRequestPayload'

type Params = {
  offerId: number
  formValues: RequestFormValues
}

type CreateCollectiveRequestAdapter = Adapter<Params, null, null>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message:
    'Impossible de créer la demande.\nVeuillez contacter le support pass culture',
  payload: null,
}

export const createCollectiveRequestAdapter: CreateCollectiveRequestAdapter =
  async ({ offerId, formValues }) => {
    try {
      const payload = createCollectiveRequestPayload(formValues)
      await apiAdage.createCollectiveRequest(offerId, payload)

      return {
        isOk: true,
        message: 'Votre demande a bien été envoyée',
        payload: null,
      }
    } catch (error) {
      return FAILING_RESPONSE
    }
  }
