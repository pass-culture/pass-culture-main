import { useLocation } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { IndividualBookingsComponent } from '@/components/Bookings/IndividualBookings'

import { getFilteredIndividualBookingsAdapter } from './adapters/getFilteredIndividualBookingsAdapter'

export const IndividualBookings = (): JSX.Element => {
  const location = useLocation()

  return (
    <BasicLayout mainHeading="Réservations individuelles">
      <IndividualBookingsComponent
        getFilteredBookingsAdapter={getFilteredIndividualBookingsAdapter}
        locationState={location.state}
      />
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualBookings
