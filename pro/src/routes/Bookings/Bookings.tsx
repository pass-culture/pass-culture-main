import React from 'react'
import { useLocation } from 'react-router-dom'

import { getVenuesAdapter } from 'core/Bookings/adapters'
import { Audience } from 'core/shared'
import BookingsScreen from 'screens/Bookings'

import {
  getBookingsCSVFileAdapter,
  getBookingsXLSFileAdapter,
  getFilteredBookingsRecapAdapter,
  getUserHasBookingsAdapter,
} from './adapters'

export type BookingsRouterState = { statuses: string[] }

const Bookings = (): JSX.Element => {
  const location = useLocation<BookingsRouterState | undefined>()

  return (
    <BookingsScreen
      audience={Audience.INDIVIDUAL}
      getBookingsCSVFileAdapter={getBookingsCSVFileAdapter}
      getBookingsXLSFileAdapter={getBookingsXLSFileAdapter}
      getFilteredBookingsRecapAdapter={getFilteredBookingsRecapAdapter}
      getUserHasBookingsAdapter={getUserHasBookingsAdapter}
      getVenuesAdapter={getVenuesAdapter}
      locationState={location.state}
    />
  )
}

export default Bookings
