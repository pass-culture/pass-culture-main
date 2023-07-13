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
import Tabs from 'ui-kit/Tabs'
import { getDefaultFacetFilterUAICodeValue } from 'utils/facetFilters'

import { populateFacetFilters } from '../utils'

import { OfferFilters } from './OfferFilters/OfferFilters'
import { Offers } from './Offers/Offers'

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
  const { removeQuery } = useContext(AlgoliaQueryContext)
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
      icon: strokeOffersIcon,
    },
    {
      label: 'Partagé avec mon établissement',
      key: OfferTab.ASSOCIATED_TO_INSTITUTION,
      onClick: () => handleTabChange(OfferTab.ASSOCIATED_TO_INSTITUTION),
      icon: strokeVenueIcon,
    },
  ]

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
      <OfferFilters
        className="search-filters"
        isLoading={isLoading}
        refine={refine}
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
