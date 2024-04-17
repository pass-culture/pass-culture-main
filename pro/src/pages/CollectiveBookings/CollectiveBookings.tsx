import React from 'react'
import { useLocation } from 'react-router-dom'

import { AppLayout } from 'app/AppLayout'
import { getVenuesAdapter } from 'core/Bookings/adapters'
import { Audience } from 'core/shared'
import BookingsScreen from 'screens/Bookings'

import {
  getFilteredCollectiveBookingsRecapAdapter,
  getUserHasCollectiveBookingsAdapter,
} from './adapters'

const CollectiveBookings = (): JSX.Element => {
  const location = useLocation()

  return (
    <AppLayout>
      <BookingsScreen
        audience={Audience.COLLECTIVE}
        getFilteredBookingsRecapAdapter={
          getFilteredCollectiveBookingsRecapAdapter
        }
        getUserHasBookingsAdapter={getUserHasCollectiveBookingsAdapter}
        getVenuesAdapter={getVenuesAdapter}
        locationState={location.state}
      />
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = CollectiveBookings
