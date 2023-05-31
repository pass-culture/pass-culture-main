import { api } from 'apiClient/api'
import { GetCollectiveOfferRequestResponseModel } from 'apiClient/v1/models/GetCollectiveOfferRequestResponseModel'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

type OfferRequestAdapter = Adapter<
  number,
  GetCollectiveOfferRequestResponseModel,
  null
>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: null,
}

export const getOfferRequestInformationsAdapter: OfferRequestAdapter = async (
  requestId: number
) => {
  try {
    const response = await api.getCollectiveOfferRequest(requestId)

    return {
      isOk: true,
      message: null,
      payload: response,
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}

export default getOfferRequestInformationsAdapter
