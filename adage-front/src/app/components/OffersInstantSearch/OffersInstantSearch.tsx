import algoliasearch from 'algoliasearch/lite'
import React, { useContext } from 'react'
import { Configure, InstantSearch } from 'react-instantsearch-dom'

import { FacetFiltersContext } from 'app/providers'
import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_OFFERS_INDEX,
} from 'utils/config'
import { Role, VenueFilterType } from 'utils/types'

import { OffersSearch } from './OffersSearch/OffersSearch'

const searchClient = algoliasearch(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
const attributesToRetrieve = [
  'objectID',
  'offer.dates',
  'offer.name',
  'offer.thumbUrl',
  'venue.name',
  'venue.publicName',
]

export const OffersInstantSearch = ({
  userRole,
  removeVenueFilter,
  venueFilter,
}: {
  userRole: Role
  removeVenueFilter: () => void
  venueFilter: VenueFilterType | null
}): JSX.Element => {
  const { facetFilters } = useContext(FacetFiltersContext)

  return (
    <InstantSearch indexName={ALGOLIA_OFFERS_INDEX} searchClient={searchClient}>
      <Configure
        attributesToHighlight={[]}
        attributesToRetrieve={attributesToRetrieve}
        facetFilters={facetFilters}
        hitsPerPage={8}
      />
      <OffersSearch
        removeVenueFilter={removeVenueFilter}
        userRole={userRole}
        venueFilter={venueFilter}
      />
    </InstantSearch>
  )
}
