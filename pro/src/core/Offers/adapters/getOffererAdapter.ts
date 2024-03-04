import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

type Payload = GetOffererResponseModel

type GetOffererAdapter = Adapter<string, Payload, null>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: null,
}

const getOffererAdapter: GetOffererAdapter = async (offererId: string) => {
  try {
    const offerer = await api.getOfferer(Number(offererId))

    return {
      isOk: true,
      message: null,
      payload: offerer,
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}

export default getOffererAdapter
