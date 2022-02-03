import './OffersSearch.scss'
import * as React from 'react'
import {
  Dispatch,
  SetStateAction,
  useCallback,
  useEffect,
  useReducer,
  useState,
} from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'
import { connectSearchBox } from 'react-instantsearch-dom'

import {
  INITIAL_FACET_FILTERS,
  INITIAL_FILTERS,
  INITIAL_QUERY,
} from 'app/constants'
import { Facets, Filters } from 'app/types'
import { Role, VenueFilterType } from 'utils/types'

import { populateFacetFilters } from '../utils'

import { filtersReducer } from './filtersReducer'
import { Offers } from './Offers/Offers'
import Pagination from './Offers/Pagination'
import OffersSearchBarAndFilters from './OffersSearchBarAndFilters'

interface SearchProps extends SearchBoxProvided {
  userRole: Role
  removeVenueFilter: () => void
  venueFilter: VenueFilterType | null
  setFacetFilters: Dispatch<SetStateAction<Facets>>
  facetFilters: Facets
}

export const OffersSearchComponent = ({
  userRole,
  removeVenueFilter,
  venueFilter,
  setFacetFilters,
  facetFilters,
  refine,
}: SearchProps): JSX.Element => {
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [query, setQuery] = useState(INITIAL_QUERY)
  const [currentFilters, dispatchCurrentFilters] = useReducer(
    filtersReducer,
    INITIAL_FILTERS
  )

  const handleSearchButtonClick = (filters: Filters): void => {
    setIsLoading(true)
    setFacetFilters(populateFacetFilters({ ...filters, venueFilter }))
  }

  const handleResetFiltersAndLaunchSearch = useCallback(() => {
    setQuery(INITIAL_QUERY)
    removeVenueFilter()
    dispatchCurrentFilters({ type: 'RESET_CURRENT_FILTERS', value: {} })
    setFacetFilters([...INITIAL_FACET_FILTERS])
    refine(INITIAL_QUERY)
  }, [refine, removeVenueFilter, setFacetFilters])

  useEffect(() => {
    if (venueFilter?.id) {
      setFacetFilters([...INITIAL_FACET_FILTERS, `venue.id:${venueFilter.id}`])
    }
  }, [venueFilter])

  return (
    <>
      <OffersSearchBarAndFilters
        currentFilters={currentFilters}
        dispatchCurrentFilters={dispatchCurrentFilters}
        handleSearchButtonClick={handleSearchButtonClick}
        isLoading={isLoading}
        query={query}
        refine={refine}
        removeVenueFilter={removeVenueFilter}
        setQuery={setQuery}
        venueFilter={venueFilter}
      />
      <div className="search-results">
        <Offers
          facetFilters={facetFilters}
          handleResetFiltersAndLaunchSearch={handleResetFiltersAndLaunchSearch}
          query={query}
          setIsLoading={setIsLoading}
          userRole={userRole}
        />
      </div>
      <Pagination />
    </>
  )
}

export const OffersSearch = connectSearchBox<SearchProps>(OffersSearchComponent)
