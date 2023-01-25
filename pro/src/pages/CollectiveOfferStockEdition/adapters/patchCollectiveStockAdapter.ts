import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { CollectiveStockResponseModel } from 'apiClient/v1'
import {
  OfferEducationalStockFormValues,
  createPatchStockDataPayload,
  CollectiveOffer,
} from 'core/OfferEducational'

type Params = {
  offer: CollectiveOffer
  stockId: string
  values: OfferEducationalStockFormValues
  initialValues: OfferEducationalStockFormValues
}

type PatchCollectiveStockAdapter = Adapter<
  Params,
  CollectiveStockResponseModel,
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

const patchCollectiveStockAdapter: PatchCollectiveStockAdapter = async ({
  offer,
  stockId,
  values,
  initialValues,
}: Params) => {
  const patchStockPayload = createPatchStockDataPayload(
    values,
    offer.venue.departementCode ?? '',
    initialValues
  )
  try {
    const stock = await api.editCollectiveStock(stockId, patchStockPayload)
    return {
      isOk: true,
      message: 'Vos modifications ont bien été enregistrées',
      payload: stock,
    }
  } catch (error) {
    if (isErrorAPIError(error) && error.status === 400) {
      return BAD_REQUEST_FAILING_RESPONSE
    } else {
      return UNKNOWN_FAILING_RESPONSE
    }
  }
}

export default patchCollectiveStockAdapter
