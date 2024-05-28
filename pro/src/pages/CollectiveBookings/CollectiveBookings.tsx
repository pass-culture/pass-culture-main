import React from 'react'
import { useLocation } from 'react-router-dom'

import { AppLayout } from 'app/AppLayout'
import { Audience } from 'core/shared/types'
import { BookingsScreen } from 'screens/Bookings/Bookings'

import { getFilteredCollectiveBookingsAdapter } from './adapters/getFilteredCollectiveBookingsAdapter'
import { getUserHasCollectiveBookingsAdapter } from './adapters/getUserHasCollectiveBookingsAdapter'

const CollectiveBookings = (): JSX.Element => {
  const location = useLocation()

  return (
    <AppLayout>
      <BookingsScreen
        audience={Audience.COLLECTIVE}
        getFilteredBookingsAdapter={getFilteredCollectiveBookingsAdapter}
        getUserHasBookingsAdapter={getUserHasCollectiveBookingsAdapter}
        locationState={location.state}
      />
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = CollectiveBookings
