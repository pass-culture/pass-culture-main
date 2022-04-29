import './OffersSearch.scss'
import * as React from 'react'
import { useEffect, useContext, useState } from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'
import { connectSearchBox } from 'react-instantsearch-dom'

import { LEGACY_INITIAL_FACET_FILTERS, INITIAL_QUERY } from 'app/constants'
import { FacetFiltersContext, AlgoliaQueryContext } from 'app/providers'
import { FiltersContext } from 'app/providers/FiltersContextProvider'
import { Filters } from 'app/types'
import { VenueFilterType } from 'app/types/offers'
import { Role } from 'utils/types'

import { populateFacetFilters } from '../utils'

import { OfferFilters } from './OfferFilters/OfferFilters'
import { Offers } from './Offers/Offers'
import { Pagination } from './Offers/Pagination'
import { SearchBox } from './SearchBox/SearchBox'

export interface SearchProps extends SearchBoxProvided {
  userRole: Role
  removeVenueFilter: () => void
  venueFilter: VenueFilterType | null
  useNewAlgoliaIndex: boolean
}

export const OffersSearchComponent = ({
  userRole,
  removeVenueFilter,
  venueFilter,
  refine,
  useNewAlgoliaIndex,
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
    if (useNewAlgoliaIndex) {
      setFacetFilters([])
    } else {
      setFacetFilters([...LEGACY_INITIAL_FACET_FILTERS])
    }
    refine(INITIAL_QUERY)
  }

  useEffect(() => {
    if (venueFilter?.id) {
      if (useNewAlgoliaIndex) {
        setFacetFilters([`venue.id:${venueFilter.id}`])
      } else {
        setFacetFilters([
          ...LEGACY_INITIAL_FACET_FILTERS,
          `venue.id:${venueFilter.id}`,
        ])
      }
    }
  }, [setFacetFilters, venueFilter, useNewAlgoliaIndex])

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
          useNewAlgoliaIndex={useNewAlgoliaIndex}
          userRole={userRole}
        />
      </div>
      <Pagination />
    </>
  )
}

export const OffersSearch = connectSearchBox<SearchProps>(OffersSearchComponent)
