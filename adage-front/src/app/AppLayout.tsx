import './AppLayout.scss'
import * as React from 'react'

import { OffersInstantSearch } from 'app/components/OffersInstantSearch/OffersInstantSearch'
import { ReactComponent as Logo } from 'assets/logo-with-text.svg'
import { Role, VenueFilterType } from 'utils/types'

export const AppLayout = ({
  userRole,
  removeVenueFilter,
  venueFilter,
}: {
  userRole: Role
  removeVenueFilter: () => void
  venueFilter: VenueFilterType | null
}): JSX.Element => {
  return (
    <main className="app-layout">
      <div className="offers-search-header">
        <h2 className="offers-search-title">Rechercher une offre</h2>
        <Logo className="app-logo" />
      </div>
      <OffersInstantSearch
        removeVenueFilter={removeVenueFilter}
        userRole={userRole}
        venueFilter={venueFilter}
      />
    </main>
  )
}
