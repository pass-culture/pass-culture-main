import './OffersSearch.scss'
import algoliasearch from 'algoliasearch/lite'
import * as React from 'react'
import { useEffect, useState } from 'react'
import { Configure, InstantSearch } from 'react-instantsearch-dom'

import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_OFFERS_INDEX,
} from 'utils/config'
import { Role, VenueFilterType } from 'utils/types'

import { Option } from '../../types'
import { Facets } from '../../types/facets'

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
  const initialFilters = ['offer.isEducational:true']
  const [facetFilters, setFacetFilters] = useState<Facets>(initialFilters)

  const handleSearchButtonClick = (departments: Option[]): void => {
    const updatedFilters: Facets = [...initialFilters]
    const filteredDepartments: string[] = departments.map(
      department => `venue.departementCode:${department.value}`
    )
    if (filteredDepartments.length > 0) {
      updatedFilters.push(filteredDepartments)
    }
    if (venueFilter?.id) {
      updatedFilters.push(`venue.id:${venueFilter.id}`)
    }
    setFacetFilters(updatedFilters)
  }

  useEffect(() => {
    if (venueFilter?.id) {
      setFacetFilters([...initialFilters, `venue.id:${venueFilter.id}`])
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [venueFilter])

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
        <OfferFilters
          className="search-filters"
          handleSearchButtonClick={handleSearchButtonClick}
          removeVenueFilter={removeVenueFilter}
          venueFilter={venueFilter}
        />
        <div className="search-results">
          <Offers userRole={userRole} />
        </div>
        <Pagination />
      </InstantSearch>
    </>
  )
}
