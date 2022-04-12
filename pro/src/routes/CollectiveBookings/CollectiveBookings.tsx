import React from 'react'
import { useLocation } from 'react-router-dom'

import { getVenuesAdapter } from 'core/Bookings/adapters'
import { Audience } from 'core/shared'
import BookingsScreen from 'screens/Bookings'

import {
  getCollectiveBookingsCSVFileAdapter,
  getFilteredCollectiveBookingsRecapAdapter,
  getUserHasCollectiveBookingsAdapter,
} from './adapters'

export type CollectiveBookingsRouterState = {
  venueId?: string
  statuses?: string[]
}

const CollectiveBookings = (): JSX.Element => {
  const location = useLocation<CollectiveBookingsRouterState>()

  return (
    <BookingsScreen
      audience={Audience.COLLECTIVE}
      getBookingsCSVFileAdapter={getCollectiveBookingsCSVFileAdapter}
      getFilteredBookingsRecapAdapter={
        getFilteredCollectiveBookingsRecapAdapter
      }
      getUserHasBookingsAdapter={getUserHasCollectiveBookingsAdapter}
      getVenuesAdapter={getVenuesAdapter}
      locationState={location.state}
      venueId={location.state?.venueId}
    />
  )
}

export default CollectiveBookings
