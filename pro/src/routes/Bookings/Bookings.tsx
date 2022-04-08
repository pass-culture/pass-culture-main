import React from 'react'
import { useLocation } from 'react-router-dom'

import { Audience } from 'core/shared'
import BookingsScreen from 'screens/Bookings'

import {
  getUserHasBookingsAdapter,
  getVenuesAdapter,
  getBookingsCSVFileAdapter,
  getFilteredBookingsRecapAdapter,
} from './adapters'

export type BookingsRouterState = { venueId?: string; statuses?: string[] }

const Bookings = (): JSX.Element => {
  const location = useLocation<BookingsRouterState>()

  return (
    <BookingsScreen
      audience={Audience.INDIVIDUAL}
      getBookingsCSVFileAdapter={getBookingsCSVFileAdapter}
      getFilteredBookingsRecapAdapter={getFilteredBookingsRecapAdapter}
      getUserHasBookingsAdapter={getUserHasBookingsAdapter}
      getVenuesAdapter={getVenuesAdapter}
      locationState={location.state}
      venueId={location.state?.venueId}
    />
  )
}

export default Bookings
