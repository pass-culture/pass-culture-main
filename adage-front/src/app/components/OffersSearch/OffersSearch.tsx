import './OffersSearch.scss'
import algoliasearch from 'algoliasearch/lite'
import * as React from 'react'
import { useEffect, useState } from 'react'
import { Configure, InstantSearch } from 'react-instantsearch-dom'

import { Facets, Option } from 'app/types'
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

const initialFilters = ['offer.isEducational:true']

export const OffersSearch = ({
  userRole,
  removeVenueFilter,
  venueFilter,
}: {
  userRole: Role
  removeVenueFilter: () => void
  venueFilter: VenueFilterType | null
}): JSX.Element => {
  const [facetFilters, setFacetFilters] = useState<Facets>(initialFilters)
  const [isLoading, setIsLoading] = useState<boolean>(false)

  const handleSearchButtonClick = (
    departments: Option[],
    students: Option[]
  ): void => {
    setIsLoading(true)
    const updatedFilters: Facets = [...initialFilters]
    const filteredDepartments: string[] = departments.map(
      department => `venue.departmentCode:${department.value}`
    )
    const filteredStudents: string[] = students.map(
      student => `offer.students:${student.value}`
    )

    if (filteredDepartments.length > 0) {
      updatedFilters.push(filteredDepartments)
    }
    if (filteredStudents.length > 0) {
      updatedFilters.push(filteredStudents)
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
          isLoading={isLoading}
          removeVenueFilter={removeVenueFilter}
          venueFilter={venueFilter}
        />
        <div className="search-results">
          <Offers setIsLoading={setIsLoading} userRole={userRole} />
        </div>
        <Pagination />
      </InstantSearch>
    </>
  )
}
