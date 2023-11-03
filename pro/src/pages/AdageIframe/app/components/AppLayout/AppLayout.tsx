import algoliasearch from 'algoliasearch/lite'
import * as React from 'react'
import { Configure, InstantSearch } from 'react-instantsearch'
import { Route, Routes, useLocation } from 'react-router-dom'

import { VenueResponse } from 'apiClient/adage'
import useActiveFeature from 'hooks/useActiveFeature'
import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_COLLECTIVE_OFFERS_INDEX,
} from 'utils/config'

import useAdageUser from '../../hooks/useAdageUser'
import { routesAdage, oldRoutesAdage } from '../../subRoutesAdage'
import { AdageHeader } from '../AdageHeader/AdageHeader'

import styles from './AppLayout.module.scss'

export const AppLayout = ({
  venueFilter,
}: {
  venueFilter: VenueResponse | null
}): JSX.Element => {
  const { adageUser } = useAdageUser()
  const { pathname } = useLocation()

  const isDiscoveryPage = pathname.includes('decouverte')
  const isDiscoveryActive = useActiveFeature('WIP_ENABLE_DISCOVERY')

  const allRoutesAdage = isDiscoveryActive ? routesAdage : oldRoutesAdage

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
          facetFilters={[
            `offer.educationalInstitutionUAICode:${adageUser.uai}`,
          ]}
          hitsPerPage={8}
          distinct={false}
        />
        <AdageHeader />
      </InstantSearch>
      <main
        className={isDiscoveryPage ? '' : styles['app-layout-content']}
        id="content"
      >
        <Routes>
          {allRoutesAdage.map(({ path, element }) => {
            // FIX ME : we pass props to routesAdage until we put those props in a context or store
            const Component = element
            return (
              <Route
                key={path}
                path={path}
                element={<Component venueFilter={venueFilter} />}
              />
            )
          })}
        </Routes>
      </main>
    </div>
  )
}
