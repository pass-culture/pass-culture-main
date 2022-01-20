import './AppLayout.scss'
import * as React from 'react'

import { Role, VenueFilterType } from 'utils/types'

import { OffersSearch } from './components/OffersSearch/OffersSearch'

export const AppLayout = ({
  userRole,
  removeVenueFilter,
  venueFilter,
}: {
  userRole: Role
  removeVenueFilter: () => void
  venueFilter: VenueFilterType | null
}): JSX.Element => (
  <main className="app-layout">
    <OffersSearch
      removeVenueFilter={removeVenueFilter}
      userRole={userRole}
      venueFilter={venueFilter}
    />
  </main>
)
