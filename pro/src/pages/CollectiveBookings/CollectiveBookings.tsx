import React from 'react'
import { useLocation } from 'react-router-dom'

import { getVenuesAdapter } from 'core/Bookings/adapters'
import { Audience } from 'core/shared'
import BookingsScreen from 'screens/Bookings'

import {
  getCollectiveBookingsCSVFileAdapter,
  getCollectiveBookingsXLSFileAdapter,
  getFilteredCollectiveBookingsRecapAdapter,
  getUserHasCollectiveBookingsAdapter,
} from './adapters'

const CollectiveBookings = (): JSX.Element => {
  const location = useLocation()

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
