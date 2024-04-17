import React from 'react'
import { useLocation } from 'react-router-dom'

import { AppLayout } from 'app/AppLayout'
import { getVenuesAdapter } from 'core/Bookings/adapters'
import { Audience } from 'core/shared'
import BookingsScreen from 'screens/Bookings'

import {
  getFilteredBookingsRecapAdapter,
  getUserHasBookingsAdapter,
} from './adapters'

export const Bookings = (): JSX.Element => {
  const location = useLocation()

  return (
    <AppLayout>
      <BookingsScreen
        audience={Audience.INDIVIDUAL}
        getFilteredBookingsRecapAdapter={getFilteredBookingsRecapAdapter}
        getUserHasBookingsAdapter={getUserHasBookingsAdapter}
        getVenuesAdapter={getVenuesAdapter}
        locationState={location.state}
      />
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Bookings
