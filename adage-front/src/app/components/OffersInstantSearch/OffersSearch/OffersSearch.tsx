import './OffersSearch.scss'
import * as React from 'react'
import { useEffect, useContext, useState } from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'
import type { StatsProvided } from 'react-instantsearch-core'
import { connectSearchBox } from 'react-instantsearch-dom'
import { connectStats } from 'react-instantsearch-dom'

import { VenueResponse } from 'apiClient'
import { AuthenticatedResponse } from 'apiClient'
import { api } from 'apiClient/api'
import { INITIAL_QUERY } from 'app/constants'
import { FacetFiltersContext, AlgoliaQueryContext } from 'app/providers'
import { FiltersContext } from 'app/providers/FiltersContextProvider'
import { Filters } from 'app/types'
import Tabs from 'app/ui-kit/Tabs'
import { ReactComponent as InstitutionIcon } from 'assets/institution.svg'
import { ReactComponent as OffersIcon } from 'assets/offers.svg'
import { LOGS_DATA } from 'utils/config'
import { getDefaultFacetFilterUAICodeValue } from 'utils/facetFilters'

import { populateFacetFilters } from '../utils'

import { OfferFilters } from './OfferFilters/OfferFilters'
import { Offers } from './Offers/Offers'
import { SearchBox } from './SearchBox/SearchBox'

export interface SearchProps extends SearchBoxProvided, StatsProvided {
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
  nbHits,
}: SearchProps): JSX.Element => {
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [activeTab, setActiveTab] = useState(OfferTab.ALL)

  const { dispatchCurrentFilters, currentFilters } = useContext(FiltersContext)
  const { setFacetFilters } = useContext(FacetFiltersContext)
  const { query, removeQuery, setQueryTag } = useContext(AlgoliaQueryContext)

  const userUAICode = user.uai
  const uaiCodeAllInstitutionsTab = userUAICode ? ['all', userUAICode] : ['all']
  const uaiCodeShareWithMyInstitutionTab = userUAICode ? [userUAICode] : null

  const handleTabChange = (tab: OfferTab) => {
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
      api.logSearchButtonClick({
        filters: updatedFilters.filtersKeys,
        resultsCount: nbHits,
      })
    }
    setQueryTag(query)
    refine(query)
  }

  const handleResetFiltersAndLaunchSearch = () => {
    setIsLoading(true)
    removeQuery()
    removeVenueFilter()
    dispatchCurrentFilters({ type: 'RESET_CURRENT_FILTERS' })
    setFacetFilters(
      activeTab === OfferTab.ASSOCIATED_TO_INSTITUTION
        ? [`offer.educationalInstitutionUAICode:${user.uai}`]
        : [getDefaultFacetFilterUAICodeValue(user.uai)]
    )
    refine(INITIAL_QUERY)
  }

  useEffect(() => {
    if (venueFilter?.id) {
      setFacetFilters([
        `venue.id:${venueFilter.id}`,
        getDefaultFacetFilterUAICodeValue(user.uai),
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

export const OffersSearch = connectStats(
  connectSearchBox<SearchProps>(OffersSearchComponent)
)
