import './AppLayout.scss'
import { useMatomo } from '@datapunt/matomo-tracker-react'
import * as React from 'react'

import { AuthenticatedResponse, VenueResponse } from 'api/gen'
import { OffersInstantSearch } from 'app/components/OffersInstantSearch/OffersInstantSearch'
import { ReactComponent as Download } from 'assets/download.svg'
import { ReactComponent as Logo } from 'assets/logo-with-text.svg'

import { getAnonymisedUserId, trackPageViewHelper } from './helpers'

export const AppLayout = ({
  user,
  removeVenueFilter,
  venueFilter,
}: {
  user: AuthenticatedResponse
  removeVenueFilter: () => void
  venueFilter: VenueResponse | null
}): JSX.Element => {
  const { enableLinkTracking, pushInstruction, trackPageView } = useMatomo()

  enableLinkTracking()

  const userId = getAnonymisedUserId()
  if (userId != null) {
    pushInstruction('setUserId', userId)
  }
  trackPageViewHelper(trackPageView)

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
