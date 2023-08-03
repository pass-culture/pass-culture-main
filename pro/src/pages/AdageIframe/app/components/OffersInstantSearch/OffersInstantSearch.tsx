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

export const OffersInstantSearch = ({
  removeVenueFilter,
  venueFilter,
}: {
  removeVenueFilter: () => void
  venueFilter: VenueResponse | null
}): JSX.Element => {
  const { facetFilters } = useContext(FacetFiltersContext)

  const newAdageFilters = useActiveFeature('WIP_ENABLE_NEW_ADAGE_FILTERS')
  const [query, setQuery] = useState<string>(
    newAdageFilters ? venueFilter?.publicName || venueFilter?.name || '' : ''
  )
  return (
    <InstantSearch
      indexName={ALGOLIA_COLLECTIVE_OFFERS_INDEX}
      searchClient={searchClient}
      searchState={{ query: query }}
    >
      <Configure
        attributesToHighlight={[]}
        attributesToRetrieve={attributesToRetrieve}
        clickAnalytics
        facetFilters={facetFilters}
        hitsPerPage={8}
      />
      <AnalyticsContextProvider>
        {
          /* istanbul ignore next: DEBT to fix: delete condition with ff */
          newAdageFilters ? (
            <OffersSearch venueFilter={venueFilter} setQuery={setQuery} />
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
