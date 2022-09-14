import { api } from 'apiClient/api'
import { CollectiveBookingByIdResponseModel } from 'apiClient/v1/models/CollectiveBookingByIdResponseModel'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

type GetCollectiveBookingAdapter = Adapter<
  string,
  CollectiveBookingByIdResponseModel,
  null
>

const getCollectiveBookingAdapter: GetCollectiveBookingAdapter =
  async bookingId => {
    try {
      const booking = await api.getCollectiveBookingById(bookingId)

      return {
        isOk: true,
        message: '',
        payload: booking,
      }
    } catch (e) {
      return {
        isOk: false,
        message: GET_DATA_ERROR_MESSAGE,
        payload: null,
      }
    }
  }

export default getCollectiveBookingAdapter
