import {
  getBookingsCSVFileAdapter,
  getBookingsXLSFileAdapter,
  getFilteredBookingsRecapAdapter,
  getUserHasBookingsAdapter,
} from './adapters'

import { Audience } from 'core/shared'
import BookingsScreen from 'screens/Bookings'
import React from 'react'
import { getVenuesAdapter } from 'core/Bookings/adapters'
import { useLocation } from 'react-router-dom'

export type BookingsRouterState = { venueId?: string; statuses?: string[] }

const Bookings = (): JSX.Element => {
  const location = useLocation<BookingsRouterState>()

  return (
    <BookingsScreen
      audience={Audience.INDIVIDUAL}
      getBookingsCSVFileAdapter={getBookingsCSVFileAdapter}
      getBookingsXLSFileAdapter={getBookingsXLSFileAdapter}
      getFilteredBookingsRecapAdapter={getFilteredBookingsRecapAdapter}
      getUserHasBookingsAdapter={getUserHasBookingsAdapter}
      getVenuesAdapter={getVenuesAdapter}
      locationState={location.state}
      venueId={location.state?.venueId}
    />
  )
}

export default Bookings
