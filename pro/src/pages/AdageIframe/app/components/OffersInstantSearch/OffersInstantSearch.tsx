import algoliasearch from 'algoliasearch/lite'
import React, { useContext, useState } from 'react'
import { Configure, InstantSearch } from 'react-instantsearch-dom'

import { VenueResponse } from 'apiClient/adage'
import useActiveFeature from 'hooks/useActiveFeature'
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
import { OldOffersSearch } from './OffersSearch/OldOffersSearch'

const searchClient = algoliasearch(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
const attributesToRetrieve = [
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
  removeVenueFilter,
  venueFilter,
}: {
  removeVenueFilter: () => void
  venueFilter: VenueResponse | null
}): JSX.Element => {
  const { facetFilters } = useContext(FacetFiltersContext)

  const newAdageFilters = useActiveFeature('WIP_ENABLE_NEW_ADAGE_FILTERS')

  const [geoRadius, setGeoRadius] = useState<number | null>(null)
  const adageUser = useAdageUser()

  return (
    <InstantSearch
      indexName={ALGOLIA_COLLECTIVE_OFFERS_INDEX}
      searchClient={searchClient}
    >
      <Configure
        attributesToHighlight={[]}
        attributesToRetrieve={attributesToRetrieve}
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
        aroundRadius={geoRadius ?? DEFAULT_GEO_RADIUS}
        distinct={false}
      />
      <AnalyticsContextProvider>
        {
          /* istanbul ignore next: DEBT to fix: delete condition with ff */
          newAdageFilters ? (
            <OffersSearch
              venueFilter={venueFilter}
              setGeoRadius={setGeoRadius}
            />
          ) : (
            <OldOffersSearch
              removeVenueFilter={removeVenueFilter}
              venueFilter={venueFilter}
            />
          )
        }
      </AnalyticsContextProvider>
    </InstantSearch>
  )
}
