import './OffersSearch.scss'
import * as React from 'react'
import { useEffect, useContext, useState } from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'
import { connectSearchBox } from 'react-instantsearch-dom'

import { INITIAL_FACET_FILTERS, INITIAL_QUERY } from 'app/constants'
import { FacetFiltersContext, AlgoliaQueryContext } from 'app/providers'
import { FiltersContext } from 'app/providers/FiltersContextProvider'
import { Filters } from 'app/types'
import { Role, VenueFilterType } from 'utils/types'

import { populateFacetFilters } from '../utils'

import { OfferFilters } from './OfferFilters/OfferFilters'
import { Offers } from './Offers/Offers'
import { Pagination } from './Offers/Pagination'
import { SearchBox } from './SearchBox/SearchBox'

export interface SearchProps extends SearchBoxProvided {
  userRole: Role
  removeVenueFilter: () => void
  venueFilter: VenueFilterType | null
}

export const OffersSearchComponent = ({
  userRole,
  removeVenueFilter,
  venueFilter,
  refine,
}: SearchProps): JSX.Element => {
  const [isLoading, setIsLoading] = useState<boolean>(false)

  const { dispatchCurrentFilters } = useContext(FiltersContext)
  const { setFacetFilters } = useContext(FacetFiltersContext)
  const { query, removeQuery, setQueryTag } = useContext(AlgoliaQueryContext)

  const handleLaunchSearchButton = (filters: Filters): void => {
    setIsLoading(true)
    setFacetFilters(populateFacetFilters({ ...filters, venueFilter }))
    setQueryTag(query)
    refine(query)
  }

  const handleResetFiltersAndLaunchSearch = () => {
    setIsLoading(true)
    removeQuery()
    removeVenueFilter()
    dispatchCurrentFilters({ type: 'RESET_CURRENT_FILTERS' })
    setFacetFilters([...INITIAL_FACET_FILTERS])
    refine(INITIAL_QUERY)
  }

  useEffect(() => {
    if (venueFilter?.id) {
      setFacetFilters([...INITIAL_FACET_FILTERS, `venue.id:${venueFilter.id}`])
    }
  }, [setFacetFilters, venueFilter])

  return (
    <>
      <SearchBox refine={refine} />
      <OfferFilters
        className="search-filters"
        handleLaunchSearchButton={handleLaunchSearchButton}
        isLoading={isLoading}
        removeVenueFilter={removeVenueFilter}
        venueFilter={venueFilter}
      />
      <div className="search-results">
        <Offers
          handleResetFiltersAndLaunchSearch={handleResetFiltersAndLaunchSearch}
          setIsLoading={setIsLoading}
          userRole={userRole}
        />
      </div>
      <Pagination />
    </>
  )
}

export const OffersSearch = connectSearchBox<SearchProps>(OffersSearchComponent)
