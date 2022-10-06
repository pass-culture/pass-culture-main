import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { CollectiveStockResponseModel } from 'apiClient/v1'
import {
  GetStockOfferSuccessPayload,
  OfferEducationalStockFormValues,
  createPatchStockDataPayload,
} from 'core/OfferEducational'

type Params = {
  offer: GetStockOfferSuccessPayload
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
    offer.venueDepartmentCode,
    initialValues
  )
  try {
    const stock = await api.editCollectiveStock(stockId, patchStockPayload)
    return {
      isOk: true,
      message: 'Le détail de votre stock a bien été modifié.',
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
