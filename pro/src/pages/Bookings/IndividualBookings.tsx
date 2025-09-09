import { useLocation } from 'react-router'

import { Layout } from '@/app/App/layout/Layout'
import { Audience } from '@/commons/core/shared/types'
import { IndividualBookingsComponent } from '@/components/Bookings/IndividualBookings'

import { getFilteredIndividualBookingsAdapter } from './adapters/getFilteredIndividualBookingsAdapter'

export const IndividualBookings = (): JSX.Element => {
  const location = useLocation()

  return (
    <Layout mainHeading="Réservations individuelles">
      <IndividualBookingsComponent
        audience={Audience.INDIVIDUAL}
        getFilteredBookingsAdapter={getFilteredIndividualBookingsAdapter}
        locationState={location.state}
      />
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualBookings
