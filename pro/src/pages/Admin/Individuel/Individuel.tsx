import { useLocation } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { AdminIndividualBookingsComponent } from '@/components/Bookings/AdminIndividualBookings'
import { LegalEntitySelect } from '@/components/LegalEntitySelect/LegalEntitySelect'
import { getFilteredAdminIndividualBookingsAdapter } from '@/pages/Bookings/adapters/getFilteredAdminIndividualBookingsAdapter'

export const Individuel = (): JSX.Element => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const location = useLocation()

  return (
    <BasicLayout
      mainHeading="Données d'activité - Individuel"
      isAdminArea={withSwitchVenueFeature}
    >
      {withSwitchVenueFeature && <LegalEntitySelect />}
      <AdminIndividualBookingsComponent
        getFilteredBookingsAdapter={getFilteredAdminIndividualBookingsAdapter}
        locationState={location.state}
      />
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Individuel
