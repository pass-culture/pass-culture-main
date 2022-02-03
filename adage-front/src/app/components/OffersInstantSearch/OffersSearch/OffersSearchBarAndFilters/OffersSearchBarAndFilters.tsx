import React from 'react'
import { SearchBoxProvided } from 'react-instantsearch-core'

import { Filters } from 'app/types'
import { VenueFilterType } from 'utils/types'

import { FiltersReducerAction } from '../filtersReducer'
import { OfferFilters } from '../OfferFilters/OfferFilters'
import { SearchBox } from '../SearchBox'

interface SearchAndFiltersProps {
  query: string
  setQuery: React.Dispatch<React.SetStateAction<string>>
  handleSearchButtonClick: (filters: Filters) => void
  isLoading: boolean
  removeVenueFilter: () => void
  venueFilter: VenueFilterType | null
  refine: SearchBoxProvided['refine']
  dispatchCurrentFilters: React.Dispatch<FiltersReducerAction>
  currentFilters: Filters
}

const SearchAndFiltersComponent = ({
  dispatchCurrentFilters,
  currentFilters,
  query,
  setQuery,
  handleSearchButtonClick,
  isLoading,
  removeVenueFilter,
  venueFilter,
  refine,
}: SearchAndFiltersProps): JSX.Element => {
  return (
    <>
      <SearchBox query={query} refine={refine} setQuery={setQuery} />
      <OfferFilters
        className="search-filters"
        currentFilters={currentFilters}
        dispatchCurrentFilters={dispatchCurrentFilters}
        handleSearchButtonClick={handleSearchButtonClick}
        isLoading={isLoading}
        query={query}
        refine={refine}
        removeVenueFilter={removeVenueFilter}
        venueFilter={venueFilter}
      />
    </>
  )
}

export default SearchAndFiltersComponent
