import { useLocation } from 'react-router'

import { Layout } from 'app/App/layout/Layout'
import { Audience } from 'commons/core/shared/types'
import { BookingsContainer } from 'components/Bookings/Bookings'

import { getFilteredIndividualBookingsAdapter } from './adapters/getFilteredIndividualBookingsAdapter'
import { getUserHasIndividualBookingsAdapter } from './adapters/getUserHasIndividualBookingsAdapter'

export const Bookings = (): JSX.Element => {
  const location = useLocation()

  return (
    <Layout>
      <BookingsContainer
        audience={Audience.INDIVIDUAL}
        getFilteredBookingsAdapter={getFilteredIndividualBookingsAdapter}
        getUserHasBookingsAdapter={getUserHasIndividualBookingsAdapter}
        locationState={location.state}
      />
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Bookings
