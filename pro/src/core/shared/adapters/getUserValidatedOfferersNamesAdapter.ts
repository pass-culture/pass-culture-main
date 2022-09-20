import { api } from 'apiClient/api'
import { GetOffererNameResponseModel } from 'apiClient/v1'

import { GET_DATA_ERROR_MESSAGE } from '../constants'

type GetUserValidatedOfferersNamesAdapter = Adapter<
  void,
  GetOffererNameResponseModel[],
  GetOffererNameResponseModel[]
>

const getUserValidatedOfferersNamesAdapter: GetUserValidatedOfferersNamesAdapter =
  async () => {
    try {
      const response = await api.listOfferersNames(undefined, true)
      return {
        isOk: true,
        message: '',
        payload: response.offerersNames,
      }
    } catch (e) {
      return { isOk: false, message: GET_DATA_ERROR_MESSAGE, payload: [] }
    }
  }

export default getUserValidatedOfferersNamesAdapter
