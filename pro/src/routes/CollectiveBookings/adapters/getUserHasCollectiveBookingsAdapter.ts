import * as pcapi from 'repository/pcapi/pcapi'

import { GetUserHasBookingsAdapter } from 'core/Bookings'

const FAILING_RESPONSE: AdapterFailure<boolean> = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: false,
}

export const getUserHasCollectiveBookingsAdapter: GetUserHasBookingsAdapter =
  async () => {
    try {
      const { hasBookings } = await pcapi.getUserHasCollectiveBookings()

      return {
        isOk: true,
        message: null,
        payload: hasBookings,
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }

export default getUserHasCollectiveBookingsAdapter
