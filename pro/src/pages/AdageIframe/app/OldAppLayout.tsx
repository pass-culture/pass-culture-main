import './OldAppLayout.scss'

import * as React from 'react'

import { VenueResponse } from 'apiClient/adage'
import logoPassCultureIcon from 'icons/logo-pass-culture.svg'
import strokeDownloadIcon from 'icons/stroke-download.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { OffersInstantSearch } from './components/OffersInstantSearch/OffersInstantSearch'

export const OldAppLayout = ({
  removeVenueFilter,
  venueFilter,
}: {
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
              <SvgIcon
                alt=""
                src={strokeDownloadIcon}
                className="app-layout-header-help-link-icon"
              />
              Télécharger l’aide
            </a>
          </div>
          <SvgIcon
            src={logoPassCultureIcon}
            alt=""
            viewBox="0 0 71 24"
            className="app-logo"
          />
        </div>

        <OffersInstantSearch
          removeVenueFilter={removeVenueFilter}
          venueFilter={venueFilter}
        />
      </main>
    </div>
  )
}
