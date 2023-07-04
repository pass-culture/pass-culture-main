import './OffersSearch.scss'

import { useContext, useState, useCallback } from 'react'
import * as React from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'
import { connectSearchBox } from 'react-instantsearch-dom'

import { VenueResponse } from 'apiClient/adage'
import useActiveFeature from 'hooks/useActiveFeature'
import { ReactComponent as InstitutionIcon } from 'icons/ico-institution.svg'
import { ReactComponent as StrokeOffersIcon } from 'icons/stroke-offers.svg'
import { INITIAL_QUERY } from 'pages/AdageIframe/app/constants'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
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

import { populateFacetFilters } from '../utils'

import { OfferFilters } from './OfferFilters/OfferFilters'
import { Offers } from './Offers/Offers'
import { SearchBox } from './SearchBox/SearchBox'

export interface SearchProps extends SearchBoxProvided {
  removeVenueFilter: () => void
  venueFilter: VenueResponse | null
}

enum OfferTab {
  ALL = 'all',
  ASSOCIATED_TO_INSTITUTION = 'associatedToInstitution',
}

export const OffersSearchComponent = ({
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
  const adageUser = useAdageUser()
  const userUAICode = adageUser.uai
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
      Icon: StrokeOffersIcon,
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
        ? [`offer.educationalInstitutionUAICode:${adageUser.uai}`]
        : [...getDefaultFacetFilterUAICodeValue(adageUser.uai)]
    )
    refine(INITIAL_QUERY)
  }, [activeTab])

  const isNewHeaderActive = useActiveFeature('WIP_ENABLE_NEW_ADAGE_HEADER')

  return (
    <>
      {!!adageUser.uai && !isNewHeaderActive && (
        <Tabs selectedKey={activeTab} tabs={tabs} />
      )}
      <SearchBox refine={refine} />
      <OfferFilters
        className="search-filters"
        handleLaunchSearchButton={handleLaunchSearchButton}
        isLoading={isLoading}
        removeVenueFilter={removeVenueFilter}
        user={adageUser}
        venueFilter={venueFilter}
      />
      <div className="search-results">
        <Offers
          handleResetFiltersAndLaunchSearch={handleResetFiltersAndLaunchSearch}
          setIsLoading={setIsLoading}
          userRole={adageUser.role}
          userEmail={adageUser.email}
        />
      </div>
    </>
  )
}

export const OffersSearch = connectSearchBox<SearchProps>(OffersSearchComponent)
