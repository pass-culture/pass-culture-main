import algoliasearch from 'algoliasearch/lite'
import React, { useContext } from 'react'
import { Configure, InstantSearch } from 'react-instantsearch-dom'

import { AuthenticatedResponse, VenueResponse } from 'api/gen'
import { useActiveFeature } from 'app/hooks/useActiveFeature'
import { FacetFiltersContext } from 'app/providers'
import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_OFFERS_INDEX,
  ALGOLIA_COLLECTIVE_OFFERS_INDEX,
} from 'utils/config'

import { OffersSearch } from './OffersSearch/OffersSearch'

const searchClient = algoliasearch(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
const attributesToRetrieve = [
  'objectID',
  'offer.dates',
  'offer.name',
  'offer.thumbUrl',
  'venue.name',
  'venue.publicName',
  'isTemplate',
]

export const OffersInstantSearch = ({
  user,
  removeVenueFilter,
  venueFilter,
}: {
  user: AuthenticatedResponse
  removeVenueFilter: () => void
  venueFilter: VenueResponse | null
}): JSX.Element => {
  const { facetFilters } = useContext(FacetFiltersContext)
  const useNewAlgoliaIndex = useActiveFeature(
    'ENABLE_NEW_ALGOLIA_INDEX_ON_ADAGE'
  )

  return (
    <InstantSearch
      indexName={
        useNewAlgoliaIndex
          ? ALGOLIA_COLLECTIVE_OFFERS_INDEX
          : ALGOLIA_OFFERS_INDEX
      }
      searchClient={searchClient}
    >
      <Configure
        attributesToHighlight={[]}
        attributesToRetrieve={attributesToRetrieve}
        facetFilters={facetFilters}
        hitsPerPage={8}
      />
      <OffersSearch
        removeVenueFilter={removeVenueFilter}
        useNewAlgoliaIndex={useNewAlgoliaIndex}
        user={user}
        venueFilter={venueFilter}
      />
    </InstantSearch>
  )
}
