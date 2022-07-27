import { GetUserHasBookingsAdapter } from 'core/Bookings'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import * as pcapi from 'repository/pcapi/pcapi'

const FAILING_RESPONSE: AdapterFailure<boolean> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: false,
}

const getFilteredBookingsRecapAdapter: GetUserHasBookingsAdapter = async () => {
  try {
    const { hasBookings } = await pcapi.getUserHasBookings()

    return {
      isOk: true,
      message: null,
      payload: hasBookings,
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}

export default getFilteredBookingsRecapAdapter
