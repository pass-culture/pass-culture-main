import { api } from 'apiClient/api'
import { Offerer } from 'core/Offers/types'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

type IPayload = Offerer

type GetOffererAdapter = Adapter<string, IPayload, null>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: null,
}

const getOffererAdapter: GetOffererAdapter = async (offererId: string) => {
  try {
    const offerer = await api.getOfferer(offererId)

    return {
      isOk: true,
      message: null,
      payload: {
        id: offerer.id,
        name: offerer.name,
      },
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}

export default getOffererAdapter
