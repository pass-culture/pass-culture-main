import {
  createPatchStockDataPayload,
  GetStockOfferSuccessPayload,
  hasStatusCode,
  OfferEducationalStockFormValues,
  StockPayload,
  StockResponse,
} from 'core/OfferEducational'
import * as pcapi from 'repository/pcapi/pcapi'

type Params = {
  offer: GetStockOfferSuccessPayload
  stockId: string
  values: OfferEducationalStockFormValues
  initialValues: OfferEducationalStockFormValues
}

type PatchCollectiveStockAdapter = Adapter<Params, StockResponse, null>

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
  const patchStockPayload: Partial<StockPayload> = createPatchStockDataPayload(
    values,
    offer.venueDepartmentCode,
    initialValues
  )
  try {
    const stock = (await pcapi.editCollectiveStock(
      stockId,
      patchStockPayload
    )) as StockResponse
    return {
      isOk: true,
      message: 'Le détail de votre stock a bien été modifié.',
      payload: stock,
    }
  } catch (error) {
    if (hasStatusCode(error) && error.status === 400) {
      return BAD_REQUEST_FAILING_RESPONSE
    } else {
      return UNKNOWN_FAILING_RESPONSE
    }
  }
}

export default patchCollectiveStockAdapter
