import './OldOffersSearch.scss'

import { useContext, useState } from 'react'
import * as React from 'react'
import { useSearchBox } from 'react-instantsearch'

import { VenueResponse } from 'apiClient/adage'
import { INITIAL_QUERY } from 'pages/AdageIframe/app/constants'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import {
  AlgoliaQueryContext,
  FacetFiltersContext,
  FiltersContext,
} from 'pages/AdageIframe/app/providers'
import { AnalyticsContext } from 'pages/AdageIframe/app/providers/AnalyticsContextProvider'
import { Filters } from 'pages/AdageIframe/app/types'
import { LOGS_DATA } from 'utils/config'
import { oldGetDefaultFacetFilterUAICodeValue } from 'utils/oldFacetFilters'

import { populateFacetFilters } from '../utils'

import { OfferFilters } from './OfferFilters/OldOfferFilters'
import { Offers } from './Offers/Offers'
import { SearchBox } from './SearchBox/SearchBox'

export interface SearchProps {
  removeVenueFilter: () => void
  venueFilter: VenueResponse | null
}

export const OldOffersSearch = ({
  removeVenueFilter,
  venueFilter,
}: SearchProps): JSX.Element => {
  const [isLoading, setIsLoading] = useState<boolean>(false)

  const { dispatchCurrentFilters } = useContext(FiltersContext)
  const { refine } = useSearchBox()
  const { setFacetFilters } = useContext(FacetFiltersContext)
  const { query, removeQuery, setQueryTag } = useContext(AlgoliaQueryContext)
  const { setFiltersKeys, setHasClickedSearch } = useContext(AnalyticsContext)
  const { adageUser } = useAdageUser()

  const handleLaunchSearchButton = (filters: Filters): void => {
    setIsLoading(true)
    const updatedFilters = populateFacetFilters({
      ...filters,
      venueFilter,
      uai: adageUser.uai ? ['all', adageUser.uai] : ['all'],
    })
    setFacetFilters(updatedFilters.queryFilters)
    /* istanbul ignore next: DEBT to fix and the file will be deleted at the same time as the ff */
    if (LOGS_DATA) {
      setFiltersKeys(updatedFilters.filtersKeys)
      setHasClickedSearch(true)
    }
    setQueryTag(query)
    refine(query)
  }

  const handleResetFiltersAndLaunchSearch = () => {
    setIsLoading(true)
    removeQuery()
    removeVenueFilter()
    dispatchCurrentFilters({ type: 'RESET_CURRENT_FILTERS' })
    /* istanbul ignore next: DEBT to fix and the file will be deleted at the same time as the ff */
    setFacetFilters([...oldGetDefaultFacetFilterUAICodeValue(adageUser.uai)])
    refine(INITIAL_QUERY)
  }

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
        />
      </div>
    </>
  )
}
