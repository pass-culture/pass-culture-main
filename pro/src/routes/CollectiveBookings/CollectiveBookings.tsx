import {
  getCollectiveBookingsCSVFileAdapter,
  getCollectiveBookingsXLSFileAdapter,
  getFilteredCollectiveBookingsRecapAdapter,
  getUserHasCollectiveBookingsAdapter,
} from './adapters'

import { Audience } from 'core/shared'
import BookingsScreen from 'screens/Bookings'
import React from 'react'
import { getVenuesAdapter } from 'core/Bookings/adapters'
import { useLocation } from 'react-router-dom'

export type CollectiveBookingsRouterState = {
  statuses?: string[]
}

const CollectiveBookings = (): JSX.Element => {
  const location = useLocation<CollectiveBookingsRouterState>()

  return (
    <BookingsScreen
      audience={Audience.COLLECTIVE}
      getBookingsCSVFileAdapter={getCollectiveBookingsCSVFileAdapter}
      getBookingsXLSFileAdapter={getCollectiveBookingsXLSFileAdapter}
      getFilteredBookingsRecapAdapter={
        getFilteredCollectiveBookingsRecapAdapter
      }
      getUserHasBookingsAdapter={getUserHasCollectiveBookingsAdapter}
      getVenuesAdapter={getVenuesAdapter}
      locationState={location.state}
    />
  )
}

export default CollectiveBookings
