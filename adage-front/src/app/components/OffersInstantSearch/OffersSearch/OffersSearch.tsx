import './OffersSearch.scss'
import * as React from 'react'
import { useEffect, useContext, useState } from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'
import { connectSearchBox } from 'react-instantsearch-dom'

import { AuthenticatedResponse, VenueResponse } from 'api/gen'
import { INITIAL_QUERY } from 'app/constants'
import { useActiveFeature } from 'app/hooks/useActiveFeature'
import { FacetFiltersContext, AlgoliaQueryContext } from 'app/providers'
import { FiltersContext } from 'app/providers/FiltersContextProvider'
import { Filters } from 'app/types'
import Tabs from 'app/ui-kit/Tabs'
import { ReactComponent as InstitutionIcon } from 'assets/institution.svg'
import { ReactComponent as OffersIcon } from 'assets/offers.svg'

import { populateFacetFilters } from '../utils'

import { OfferFilters } from './OfferFilters/OfferFilters'
import { Offers } from './Offers/Offers'
import { Pagination } from './Offers/Pagination'
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

  const { dispatchCurrentFilters } = useContext(FiltersContext)
  const { setFacetFilters } = useContext(FacetFiltersContext)
  const { query, removeQuery, setQueryTag } = useContext(AlgoliaQueryContext)

  const enableEducationalInstitutionAssociation = useActiveFeature(
    'ENABLE_EDUCATIONAL_INSTITUTION_ASSOCIATION'
  )

  const tabs = [
    {
      label: 'Toutes les offres',
      key: OfferTab.ALL,
      onClick: () => setActiveTab(OfferTab.ALL),
      Icon: OffersIcon,
    },
    {
      label: 'Partagé avec mon établissement',
      key: OfferTab.ASSOCIATED_TO_INSTITUTION,
      onClick: () => setActiveTab(OfferTab.ASSOCIATED_TO_INSTITUTION),
      Icon: InstitutionIcon,
    },
  ]

  const handleLaunchSearchButton = (filters: Filters): void => {
    setIsLoading(true)
    setFacetFilters(
      populateFacetFilters({
        ...filters,
        venueFilter,
        useNewAlgoliaIndex: true,
      })
    )
    setQueryTag(query)
    refine(query)
  }

  const handleResetFiltersAndLaunchSearch = () => {
    setIsLoading(true)
    removeQuery()
    removeVenueFilter()
    dispatchCurrentFilters({ type: 'RESET_CURRENT_FILTERS' })
    setFacetFilters([])
    refine(INITIAL_QUERY)
  }

  useEffect(() => {
    if (venueFilter?.id) {
      setFacetFilters([`venue.id:${venueFilter.id}`])
    }
  }, [setFacetFilters, venueFilter])

  return (
    <>
      {enableEducationalInstitutionAssociation && !!user.uai && (
        <Tabs selectedKey={activeTab} tabs={tabs} />
      )}
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
          userRole={user.role}
        />
      </div>
      <Pagination />
    </>
  )
}

export const OffersSearch = connectSearchBox<SearchProps>(OffersSearchComponent)
