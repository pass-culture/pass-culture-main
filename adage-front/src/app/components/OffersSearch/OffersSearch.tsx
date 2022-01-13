import './OffersSearch.scss'
import algoliasearch from 'algoliasearch/lite'
import * as React from 'react'
import { Configure, InstantSearch } from 'react-instantsearch-dom'

import { VenueFilterStatus } from 'app/components/OffersSearch/VenueFilterStatus/VenueFilterStatus'
import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_OFFERS_INDEX,
} from 'utils/config'
import { Role, VenueFilterType } from 'utils/types'

import { OfferFilters } from './OfferFilters/OfferFilters'
import { Offers } from './Offers/Offers'
import Pagination from './Offers/Pagination'
import { SearchBox } from './SearchBox'

const searchClient = algoliasearch(ALGOLIA_APP_ID, ALGOLIA_API_KEY)

const attributesToRetrieve = [
  'objectID',
  'offer.dates',
  'offer.name',
  'offer.thumbUrl',
  'venue.name',
  'venue.publicName',
]

export const OffersSearch = ({
  userRole,
  removeVenueFilter,
  venueFilter,
}: {
  userRole: Role
  removeVenueFilter: () => void
  venueFilter: VenueFilterType | null
}): JSX.Element => {
  const facetFilters = ['offer.isEducational:true']
  if (venueFilter && venueFilter.id)
    facetFilters.push(`venue.id:${venueFilter.id}`)

  return (
    <>
      <h2>Rechercher une offre</h2>
      <InstantSearch
        indexName={ALGOLIA_OFFERS_INDEX}
        searchClient={searchClient}
      >
        <Configure
          attributesToHighlight={[]}
          attributesToRetrieve={attributesToRetrieve}
          facetFilters={facetFilters}
          hitsPerPage={8}
        />
        <SearchBox />
        <OfferFilters className="search-filters" />
        <div className="search-results">
          {venueFilter && (
            <VenueFilterStatus
              removeFilter={removeVenueFilter}
              venueFilter={venueFilter}
            />
          )}
          <Offers userRole={userRole} />
        </div>
        <Pagination />
      </InstantSearch>
    </>
  )
}
