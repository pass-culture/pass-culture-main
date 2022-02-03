import algoliasearch from 'algoliasearch/lite'
import React, { useState } from 'react'
import { Configure, InstantSearch } from 'react-instantsearch-dom'

import { INITIAL_FACET_FILTERS } from 'app/constants'
import { Facets } from 'app/types'
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
  const [facetFilters, setFacetFilters] = useState<Facets>([
    ...INITIAL_FACET_FILTERS,
  ])

  return (
    <InstantSearch indexName={ALGOLIA_OFFERS_INDEX} searchClient={searchClient}>
      <Configure
        attributesToHighlight={[]}
        attributesToRetrieve={attributesToRetrieve}
        facetFilters={facetFilters}
        hitsPerPage={8}
      />
      <OffersSearch
        facetFilters={facetFilters}
        removeVenueFilter={removeVenueFilter}
        setFacetFilters={setFacetFilters}
        userRole={userRole}
        venueFilter={venueFilter}
      />
    </InstantSearch>
  )
}
