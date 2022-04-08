import { GetUserHasBookingsAdapter } from 'core/Bookings'
import * as pcapi from 'repository/pcapi/pcapi'

const FAILING_RESPONSE: AdapterFailure<boolean> = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
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
