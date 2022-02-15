import { Stock } from 'custom_types'
import * as pcapi from 'repository/pcapi/pcapi'

type IPayloadSuccess = {
  stock: Stock | null
}
type IPayloadFailure = { stock: null }
type GetEducationalStockAdapter = Adapter<
  string,
  IPayloadSuccess,
  IPayloadFailure
>

const FAILING_RESPONSE: AdapterFailure<IPayloadFailure> = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: { stock: null },
}

export const getEducationalStockAdapter: GetEducationalStockAdapter =
  async offerId => {
    try {
      const { stocks } = (await pcapi.loadStocks(offerId)) as {
        stocks: Stock[]
      }
      return {
        isOk: true,
        message: '',
        payload: { stock: stocks[0] ?? null },
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }
