import React, { useState } from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'
import { connectSearchBox } from 'react-instantsearch-dom'

import { Option } from 'app/types'
import { VenueFilterType } from 'utils/types'

import { OfferFilters } from '../OfferFilters/OfferFilters'
import { SearchBox } from '../SearchBox'

interface SearchAndFiltersProps extends SearchBoxProvided {
  handleSearchButtonClick: (
    departments: Option[],
    categories: Option<string[]>[],
    students: Option[]
  ) => void
  isLoading: boolean
  removeVenueFilter: () => void
  venueFilter: VenueFilterType | null
}

export const SearchAndFiltersComponent = ({
  handleSearchButtonClick,
  isLoading,
  removeVenueFilter,
  venueFilter,
  refine,
}: SearchAndFiltersProps): JSX.Element => {
  const [query, setQuery] = useState('')

  return (
    <>
      <SearchBox query={query} refine={refine} setQuery={setQuery} />
      <OfferFilters
        className="search-filters"
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

export default connectSearchBox<SearchAndFiltersProps>(
  SearchAndFiltersComponent
)
