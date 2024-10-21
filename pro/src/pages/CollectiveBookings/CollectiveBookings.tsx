import React from 'react'
import { useLocation } from 'react-router-dom'

import { Layout } from 'app/App/layout/Layout'
import { Audience } from 'commons/core/shared/types'
import { BookingsScreen } from 'components/Bookings/Bookings'

import { getFilteredCollectiveBookingsAdapter } from './adapters/getFilteredCollectiveBookingsAdapter'
import { getUserHasCollectiveBookingsAdapter } from './adapters/getUserHasCollectiveBookingsAdapter'

const CollectiveBookings = (): JSX.Element => {
  const location = useLocation()

  return (
    <Layout>
      <BookingsScreen
        audience={Audience.COLLECTIVE}
        getFilteredBookingsAdapter={getFilteredCollectiveBookingsAdapter}
        getUserHasBookingsAdapter={getUserHasCollectiveBookingsAdapter}
        locationState={location.state}
      />
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = CollectiveBookings
