import algoliasearch from 'algoliasearch/lite'
import * as React from 'react'
import { Configure, InstantSearch } from 'react-instantsearch-dom'
import { Route, Routes } from 'react-router-dom'

import { AuthenticatedResponse, VenueResponse } from 'apiClient/adage'
import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_COLLECTIVE_OFFERS_INDEX,
} from 'utils/config'

import routesAdage from '../../subRoutesAdage'
import { AdageHeader } from '../AdageHeader/AdageHeader'

import styles from './AppLayout.module.scss'

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
    <div>
      <InstantSearch
        searchClient={algoliasearch(ALGOLIA_APP_ID, ALGOLIA_API_KEY)}
        indexName={ALGOLIA_COLLECTIVE_OFFERS_INDEX}
      >
        <Configure
          attributesToHighlight={[]}
          attributesToRetrieve={[]}
          clickAnalytics
          facetFilters={[`offer.educationalInstitutionUAICode:${user.uai}`]}
          hitsPerPage={8}
        />
        <AdageHeader />
      </InstantSearch>
      <main className={styles['app-layout-content']} id="content">
        <Routes>
          {routesAdage.map(({ path, element }) => {
            // FIX ME : we pass props to routesAdage until we put those props in a context or store
            const Component = element
            return (
              <Route
                key={path}
                path={path}
                element={
                  <Component
                    user={user}
                    venueFilter={venueFilter}
                    removeVenueFilter={removeVenueFilter}
                  />
                }
              />
            )
          })}
        </Routes>
      </main>
    </div>
  )
}
