import './OldAppLayout.scss'

import * as React from 'react'

import { AuthenticatedResponse, VenueResponse } from 'apiClient/adage'
import { ReactComponent as Download } from 'icons/ico-other-download.svg'
import { ReactComponent as Logo } from 'icons/logo-pass-culture-dark.svg'

import { OffersInstantSearch } from './components/OffersInstantSearch/OffersInstantSearch'

export const OldAppLayout = ({
  user,
  removeVenueFilter,
  venueFilter,
}: {
  user: AuthenticatedResponse
  removeVenueFilter: () => void
  venueFilter: VenueResponse | null
}): JSX.Element => {
  return (
    <div className="root-adage">
      <main className="app-layout" id="content">
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
    </div>
  )
}
