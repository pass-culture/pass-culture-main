import './OffersSearch.scss'

import { useEffect, useContext, useState, useCallback } from 'react'
import * as React from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'
import { connectSearchBox } from 'react-instantsearch-dom'

import { AuthenticatedResponse, VenueResponse } from 'apiClient/adage'
import { ReactComponent as InstitutionIcon } from 'icons/ico-institution.svg'
import { ReactComponent as OffersIcon } from 'icons/ico-offers.svg'
import { INITIAL_QUERY } from 'pages/AdageIframe/app/constants'
import {
  AlgoliaQueryContext,
  FacetFiltersContext,
  FiltersContext,
} from 'pages/AdageIframe/app/providers'
import { AnalyticsContext } from 'pages/AdageIframe/app/providers/AnalyticsContextProvider'
import { Filters } from 'pages/AdageIframe/app/types'
import Tabs from 'ui-kit/Tabs'
import { LOGS_DATA } from 'utils/config'
import { getDefaultFacetFilterUAICodeValue } from 'utils/facetFilters'

import { computeVenueFacetFilter, populateFacetFilters } from '../utils'

import { OfferFilters } from './OfferFilters/OfferFilters'
import { Offers } from './Offers/Offers'
import { SearchBox } from './SearchBox/SearchBox'

export interface SearchProps extends SearchBoxProvided {
  user: AuthenticatedResponse
  removeVenueFilter: () => void
  venueFilter: VenueResponse | null
}

enum OfferTab {
  ALL = 'all',
  ASSOCIATED_TO_INSTITUTION = 'associatedToInstitution',
}

export const OffersSearchComponent = ({
  user,
  removeVenueFilter,
  venueFilter,
  refine,
}: SearchProps): JSX.Element => {
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [activeTab, setActiveTab] = useState(OfferTab.ALL)

  const { dispatchCurrentFilters, currentFilters } = useContext(FiltersContext)
  const { setFacetFilters } = useContext(FacetFiltersContext)
  const { query, removeQuery, setQueryTag } = useContext(AlgoliaQueryContext)
  const { setFiltersKeys, setHasClickedSearch } = useContext(AnalyticsContext)

  const userUAICode = user.uai
  const uaiCodeAllInstitutionsTab = userUAICode ? ['all', userUAICode] : ['all']
  const uaiCodeShareWithMyInstitutionTab = userUAICode ? [userUAICode] : null

  const handleTabChange = (tab: OfferTab) => {
    dispatchCurrentFilters({
      type: 'RESET_CURRENT_FILTERS',
    })
    setActiveTab(tab)
    setFacetFilters(
      populateFacetFilters({
        ...currentFilters,
        venueFilter,
        uai:
          tab === OfferTab.ASSOCIATED_TO_INSTITUTION
            ? uaiCodeShareWithMyInstitutionTab
            : uaiCodeAllInstitutionsTab,
      }).queryFilters
    )
  }

  const tabs = [
    {
      label: 'Toutes les offres',
      key: OfferTab.ALL,
      onClick: () => handleTabChange(OfferTab.ALL),
      Icon: OffersIcon,
    },
    {
      label: 'Partagé avec mon établissement',
      key: OfferTab.ASSOCIATED_TO_INSTITUTION,
      onClick: () => handleTabChange(OfferTab.ASSOCIATED_TO_INSTITUTION),
      Icon: InstitutionIcon,
    },
  ]

  const handleLaunchSearchButton = (filters: Filters): void => {
    setIsLoading(true)
    const updatedFilters = populateFacetFilters({
      ...filters,
      venueFilter,
      uai:
        activeTab === OfferTab.ASSOCIATED_TO_INSTITUTION
          ? uaiCodeShareWithMyInstitutionTab
          : uaiCodeAllInstitutionsTab,
    })
    setFacetFilters(updatedFilters.queryFilters)
    if (LOGS_DATA) {
      setFiltersKeys(updatedFilters.filtersKeys)
      setHasClickedSearch(true)
    }
    setQueryTag(query)
    refine(query)
  }

  const handleResetFiltersAndLaunchSearch = useCallback(() => {
    setIsLoading(true)
    removeQuery()
    removeVenueFilter()
    dispatchCurrentFilters({ type: 'RESET_CURRENT_FILTERS' })
    setFacetFilters(
      activeTab === OfferTab.ASSOCIATED_TO_INSTITUTION
        ? [`offer.educationalInstitutionUAICode:${user.uai}`]
        : [...getDefaultFacetFilterUAICodeValue(user.uai)]
    )
    refine(INITIAL_QUERY)
  }, [activeTab])

  useEffect(() => {
    if (venueFilter?.id) {
      setFacetFilters([
        computeVenueFacetFilter(venueFilter),
        ...getDefaultFacetFilterUAICodeValue(user.uai),
      ])
    }
  }, [setFacetFilters, venueFilter, user.uai])

  return (
    <>
      {!!user.uai && <Tabs selectedKey={activeTab} tabs={tabs} />}
      <SearchBox refine={refine} />
      <OfferFilters
        className="search-filters"
        handleLaunchSearchButton={handleLaunchSearchButton}
        isLoading={isLoading}
        removeVenueFilter={removeVenueFilter}
        user={user}
        venueFilter={venueFilter}
      />
      <div className="search-results">
        <Offers
          handleResetFiltersAndLaunchSearch={handleResetFiltersAndLaunchSearch}
          setIsLoading={setIsLoading}
          userRole={user.role}
        />
      </div>
    </>
  )
}

export const OffersSearch = connectSearchBox<SearchProps>(OffersSearchComponent)
