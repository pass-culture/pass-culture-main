import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { StockResponseModel } from 'apiClient/v1'
import { OFFER_WIZARD_MODE } from 'core/Offers'

import { IStockThingFormValues } from '../'

import { serializeStockThingList } from './serializers'

type TSuccessPayload = { stockIds: string[] }
type TFailurePayload = { errors: Record<string, string> }
type TUpdateStocksAdapter = Adapter<
  {
    offerId: number
    formValues: IStockThingFormValues
    departementCode: string
    mode: OFFER_WIZARD_MODE
  },
  TSuccessPayload,
  TFailurePayload
>

const successMessage = {
  [OFFER_WIZARD_MODE.CREATION]: 'Brouillon sauvegardé dans la liste des offres',
  [OFFER_WIZARD_MODE.DRAFT]: 'Brouillon sauvegardé dans la liste des offres',
  [OFFER_WIZARD_MODE.EDITION]: 'Vos modifications ont bien été enregistrées',
}

const upsertStocksThingAdapter: TUpdateStocksAdapter = async ({
  offerId,
  formValues,
  departementCode,
  mode,
}) => {
  try {
    const response = await api.upsertStocks({
      offerId: offerId,
      stocks: serializeStockThingList(formValues, departementCode),
    })
    return {
      isOk: true,
      message: successMessage[mode],
      payload: {
        stockIds: response.stocks.map((stock: StockResponseModel) => stock.id),
      },
    }
  } catch (error) {
    let formErrors = {}
    /* istanbul ignore next */
    if (isErrorAPIError(error)) {
      formErrors = error.body
    }
    return {
      isOk: false,
      message: 'Une erreur est survenue lors de la mise à jour de votre stock',
      payload: {
        errors: serializeApiErrors(formErrors),
      },
    }
  }
}
export default upsertStocksThingAdapter
