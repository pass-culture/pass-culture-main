import './AppLayout.scss'
import * as React from 'react'

import { AuthenticatedResponse, VenueResponse } from 'apiClient'
import { OffersInstantSearch } from 'app/components/OffersInstantSearch/OffersInstantSearch'
import { ReactComponent as Download } from 'assets/download.svg'
import { ReactComponent as Logo } from 'assets/logo-with-text.svg'

export const AppLayout = ({
  user,
  removeVenueFilter,
  venueFilter,
}: {
  user: AuthenticatedResponse
  removeVenueFilter: () => void
  venueFilter: VenueResponse | null
}): JSX.Element => {
  return (
    <main className="app-layout">
      <div className="app-layout-header">
        <div className="app-layout-header-right">
          <h2 className="app-layout-header-title">Rechercher une offre</h2>
          <a
            className="app-layout-header-help-link"
            download
            href={`${document.referrer}adage/index/docGet/doc/PARCOURS_REDACTEUR`}
            rel="noreferrer"
            target="_blank"
          >
            <Download className="app-layout-header-help-link-icon" />
            Télécharger l’aide
          </a>
        </div>
        <Logo className="app-logo" />
      </div>
      <OffersInstantSearch
        removeVenueFilter={removeVenueFilter}
        user={user}
        venueFilter={venueFilter}
      />
    </main>
  )
}
