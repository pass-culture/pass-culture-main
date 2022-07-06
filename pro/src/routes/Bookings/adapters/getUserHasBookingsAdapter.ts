import * as pcapi from 'repository/pcapi/pcapi'

import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { GetUserHasBookingsAdapter } from 'core/Bookings'

const FAILING_RESPONSE: AdapterFailure<boolean> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: false,
}

export const getFilteredBookingsRecapAdapter: GetUserHasBookingsAdapter =
  async () => {
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
