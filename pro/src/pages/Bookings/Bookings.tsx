import React from 'react'
import { useLocation } from 'react-router-dom'

import { AppLayout } from 'app/AppLayout'
import { Audience } from 'core/shared/types'
import { BookingsScreen } from 'screens/Bookings/Bookings'

import { getFilteredIndividualBookingsAdapter } from './adapters/getFilteredIndividualBookingsAdapter'
import { getUserHasIndividualBookingsAdapter } from './adapters/getUserHasIndividualBookingsAdapter'

export const Bookings = (): JSX.Element => {
  const location = useLocation()

  return (
    <AppLayout>
      <BookingsScreen
        audience={Audience.INDIVIDUAL}
        getFilteredBookingsAdapter={getFilteredIndividualBookingsAdapter}
        getUserHasBookingsAdapter={getUserHasIndividualBookingsAdapter}
        locationState={location.state}
      />
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Bookings
