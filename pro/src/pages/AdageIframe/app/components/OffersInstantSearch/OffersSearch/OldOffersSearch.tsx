import './OldOffersSearch.scss'

import { useContext, useState, useCallback } from 'react'
import * as React from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'
import { connectSearchBox } from 'react-instantsearch-dom'

import { VenueResponse } from 'apiClient/adage'
import useActiveFeature from 'hooks/useActiveFeature'
import strokeOffersIcon from 'icons/stroke-offers.svg'
import strokeVenueIcon from 'icons/stroke-venue.svg'
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
import { oldGetDefaultFacetFilterUAICodeValue } from 'utils/oldFacetFilters'

import { populateFacetFilters } from '../utils'

import { OfferFilters } from './OfferFilters/OldOfferFilters'
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

export const OldOffersSearchComponent = ({
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
          /* istanbul ignore next: DEBT to fix and the file will be deleted at the same time as the ff */
          tab === OfferTab.ASSOCIATED_TO_INSTITUTION
            ? uaiCodeShareWithMyInstitutionTab
            : uaiCodeAllInstitutionsTab,
      }).queryFilters
    )
  }

  /* istanbul ignore next: DEBT to fix and the file will be deleted at the same time as the ff */
  const tabs = [
    {
      label: 'Toutes les offres',
      key: OfferTab.ALL,
      onClick: () => handleTabChange(OfferTab.ALL),
      icon: strokeOffersIcon,
    },
    {
      label: 'Partagé avec mon établissement',
      key: OfferTab.ASSOCIATED_TO_INSTITUTION,
      onClick: () => handleTabChange(OfferTab.ASSOCIATED_TO_INSTITUTION),
      icon: strokeVenueIcon,
    },
  ]

  const handleLaunchSearchButton = (filters: Filters): void => {
    setIsLoading(true)
    const updatedFilters = populateFacetFilters({
      ...filters,
      venueFilter,
      uai:
        /* istanbul ignore next: DEBT to fix and the file will be deleted at the same time as the ff */
        activeTab === OfferTab.ASSOCIATED_TO_INSTITUTION
          ? uaiCodeShareWithMyInstitutionTab
          : uaiCodeAllInstitutionsTab,
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

  const handleResetFiltersAndLaunchSearch = useCallback(() => {
    setIsLoading(true)
    removeQuery()
    removeVenueFilter()
    dispatchCurrentFilters({ type: 'RESET_CURRENT_FILTERS' })
    /* istanbul ignore next: DEBT to fix and the file will be deleted at the same time as the ff */
    setFacetFilters(
      activeTab === OfferTab.ASSOCIATED_TO_INSTITUTION
        ? [`offer.educationalInstitutionUAICode:${adageUser.uai}`]
        : [...oldGetDefaultFacetFilterUAICodeValue(adageUser.uai)]
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

export const OldOffersSearch = connectSearchBox<SearchProps>(
  OldOffersSearchComponent
)
