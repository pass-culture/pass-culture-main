import React from 'react'
import { useLocation } from 'react-router-dom'

import { getVenuesAdapter } from 'core/Bookings/adapters'
import { Audience } from 'core/shared'
import { getBookingsCSVFileAdapter } from 'routes/Bookings/adapters'
import BookingsScreen from 'screens/Bookings'

export type CollectiveBookingsRouterState = {
  venueId?: string
  statuses?: string[]
}

const CollectiveBookings = (): JSX.Element => {
  const location = useLocation<CollectiveBookingsRouterState>()

  return (
    <BookingsScreen
      audience={Audience.COLLECTIVE}
      // TODO: create adapters for collective data (PC-14125)
      getBookingsCSVFileAdapter={getBookingsCSVFileAdapter}
      getFilteredBookingsRecapAdapter={() =>
        Promise.resolve({
          isOk: true,
          message: '',
          payload: { bookings: [], pages: 0, currentPage: 1 },
        })
      }
      getUserHasBookingsAdapter={() =>
        Promise.resolve({
          isOk: true,
          message: '',
          payload: false,
        })
      }
      getVenuesAdapter={getVenuesAdapter}
      locationState={location.state}
      venueId={location.state?.venueId}
    />
  )
}

export default CollectiveBookings
