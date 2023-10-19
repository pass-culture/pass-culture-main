import algoliasearch from 'algoliasearch/lite'
import React, { useContext, useState } from 'react'
import { Configure, Index, InstantSearch } from 'react-instantsearch'

import { VenueResponse } from 'apiClient/adage'
import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_COLLECTIVE_OFFERS_INDEX,
} from 'utils/config'
import { isNumber } from 'utils/types'

import useAdageUser from '../../hooks/useAdageUser'
import { FacetFiltersContext } from '../../providers'
import { AnalyticsContextProvider } from '../../providers/AnalyticsContextProvider'

import { OffersSearch } from './OffersSearch/OffersSearch'

const searchClient = algoliasearch(ALGOLIA_APP_ID, ALGOLIA_API_KEY)

export const MAIN_INDEX_ID = 'main_offers_index'

export const algoliaSearchDefaultAttributesToRetrieve = [
  'objectID',
  'offer.dates',
  'offer.name',
  'offer.thumbUrl',
  'venue.name',
  'venue.publicName',
  'isTemplate',
  'offer.interventionArea',
]

export const DEFAULT_GEO_RADIUS = 30000000 // 30 000 km ensure we get all results in the world

export const OffersInstantSearch = ({
  venueFilter,
}: {
  venueFilter: VenueResponse | null
}): JSX.Element => {
  const { facetFilters } = useContext(FacetFiltersContext)

  const [geoRadius, setGeoRadius] = useState<number>(DEFAULT_GEO_RADIUS)
  const { adageUser } = useAdageUser()

  return (
    <InstantSearch
      indexName={ALGOLIA_COLLECTIVE_OFFERS_INDEX}
      searchClient={searchClient}
    >
      <Index
        indexName={ALGOLIA_COLLECTIVE_OFFERS_INDEX}
        indexId={MAIN_INDEX_ID}
      >
        <Configure
          attributesToHighlight={[]}
          attributesToRetrieve={algoliaSearchDefaultAttributesToRetrieve}
          clickAnalytics
          facetFilters={facetFilters}
          filters={
            'offer.eventAddressType:offererVenue<score=3> OR offer.eventAddressType:school<score=2> OR offer.eventAddressType:other<score=1>'
          }
          hitsPerPage={8}
          aroundLatLng={
            isNumber(adageUser.lat) && isNumber(adageUser.lon)
              ? `${adageUser.lat}, ${adageUser.lon}`
              : undefined
          }
          aroundRadius={geoRadius}
          distinct={false}
        />
        <AnalyticsContextProvider>
          <OffersSearch venueFilter={venueFilter} setGeoRadius={setGeoRadius} />
        </AnalyticsContextProvider>
      </Index>
    </InstantSearch>
  )
}
