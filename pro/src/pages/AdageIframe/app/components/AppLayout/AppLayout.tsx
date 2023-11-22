import algoliasearch from 'algoliasearch/lite'
import * as React from 'react'
import { Configure, InstantSearch } from 'react-instantsearch'
import { Navigate, Route, Routes, useLocation } from 'react-router-dom'

import { VenueResponse } from 'apiClient/adage'
import useActiveFeature from 'hooks/useActiveFeature'
import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_COLLECTIVE_OFFERS_INDEX,
} from 'utils/config'

import useAdageUser from '../../hooks/useAdageUser'
import { AdageDiscovery } from '../AdageDiscovery/AdageDiscovery'
import { AdageHeader } from '../AdageHeader/AdageHeader'
import { OffersFavorites } from '../OffersFavorites/OffersFavorites'
import OffersForMyInstitution from '../OffersForInstitution/OffersForMyInstitution'
import { OffersInfos } from '../OffersInfos/OffersInfos'
import { OffersInstantSearch } from '../OffersInstantSearch/OffersInstantSearch'

import styles from './AppLayout.module.scss'

export const AppLayout = ({
  venueFilter,
}: {
  venueFilter: VenueResponse | null
}): JSX.Element => {
  const { adageUser } = useAdageUser()
  const { pathname, search } = useLocation()
  const params = new URLSearchParams(search)

  const isDiscoveryPage = pathname === '/adage-iframe'
  const isDiscoveryActive = useActiveFeature('WIP_ENABLE_DISCOVERY')
  const venueId = params.get('venue')

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
          <Route
            path=""
            element={
              isDiscoveryActive && !venueId ? (
                <AdageDiscovery />
              ) : (
                <Navigate to={`recherche${search}`} />
              )
            }
          />
          <Route
            path="recherche"
            element={<OffersInstantSearch venueFilter={venueFilter} />}
          />
          <Route
            path="mon-etablissement"
            element={<OffersForMyInstitution />}
          />
          <Route path="mes-favoris" element={<OffersFavorites />} />
          <Route path="decouverte/offre/:offerId" element={<OffersInfos />} />
        </Routes>
      </main>
    </div>
  )
}
