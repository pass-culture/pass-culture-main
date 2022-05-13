import { TOffererName } from 'core/Offerers/types'
import { apiV1 } from 'api/api'

type Params = void
type IPayload = TOffererName[]
type TGetOffererNamesAdapter = Adapter<Params, IPayload, IPayload>

const FAILING_RESPONSE = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: [],
}

export const getOffererNamesAdapter: TGetOffererNamesAdapter = async () => {
  try {
    const response = await apiV1.getOfferersListOfferersNames()
    return {
      isOk: true,
      message: null,
      payload: response.offerersNames,
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}

export default getOffererNamesAdapter
