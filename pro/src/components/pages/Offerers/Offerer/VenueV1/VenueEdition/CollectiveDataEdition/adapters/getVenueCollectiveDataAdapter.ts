import { api } from 'apiClient/api'
import { GetCollectiveVenueResponseModel } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

type GetVenueCollectiveDataAdapter = Adapter<
  string,
  GetCollectiveVenueResponseModel,
  null
>

const getVenueCollectiveDataAdapter: GetVenueCollectiveDataAdapter =
  async venueId => {
    try {
      const response = await api.getVenueCollectiveData(venueId)
      return {
        isOk: true,
        message: '',
        payload: response,
      }
    } catch (e) {
      return {
        isOk: false,
        message: GET_DATA_ERROR_MESSAGE,
        payload: null,
      }
    }
  }

export default getVenueCollectiveDataAdapter
