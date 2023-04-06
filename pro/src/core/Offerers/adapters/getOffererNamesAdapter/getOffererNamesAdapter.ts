import { api } from 'apiClient/api'
import { TOffererName } from 'core/Offerers/types'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

interface IParams {
  offererId?: number
}
type TGetOffererNamesAdapter = Adapter<IParams, TOffererName[], TOffererName[]>
const FAILING_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

const getOffererNamesAdapter: TGetOffererNamesAdapter = async ({
  offererId,
}) => {
  try {
    const response = await api.listOfferersNames(
      null, // validated
      null, // validatedForUser
      offererId
    )

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
