import React, { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import ActionsBarPortal from 'components/layout/ActionsBarPortal/ActionsBarPortal'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'
import ActionsBarContainer from 'components/pages/Offers/Offers/ActionsBar/ActionsBarContainer'
import OffersContainer from 'components/pages/Offers/Offers/OffersContainer'
import {
  DEFAULT_SEARCH_FILTERS,
  hasSearchFilters,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
} from 'core/Offers'
import {
  Audience,
  Offer,
  Offerer,
  Option,
  TSearchFilters,
} from 'core/Offers/types'
import { ReactComponent as AddOfferSvg } from 'icons/ico-plus.svg'

import NoOffers from './NoOffers'
import OfferListFilterTabs from './OfferListFilterTabs'
import SearchFilters from './SearchFilters'

export interface IOffersProps {
  currentPageNumber: number
  currentUser: { isAdmin: boolean }
  isLoading: boolean
  loadAndUpdateOffers: (filters: TSearchFilters) => Promise<void>
  offerer: Offerer | null
  offers: Offer[]
  setOfferer: (offerer: Offerer | null) => void
  separateIndividualAndCollectiveOffers: boolean
  initialSearchFilters: TSearchFilters
  urlAudience: Audience
  redirectWithUrlFilters: (
    filters: TSearchFilters & {
      page?: number
      audience?: Audience
    }
  ) => void
  urlSearchFilters: TSearchFilters
  venues: Option[]
  categories: Option[]
}

const Offers = ({
  currentPageNumber,
  currentUser,
  isLoading,
  loadAndUpdateOffers,
  offerer,
  offers,
  setOfferer,
  separateIndividualAndCollectiveOffers,
  initialSearchFilters,
  urlAudience,
  redirectWithUrlFilters,
  urlSearchFilters,
  venues,
  categories,
}: IOffersProps): JSX.Element => {
  const [searchFilters, setSearchFilters] =
    useState<TSearchFilters>(initialSearchFilters)
  const [isRefreshingOffers, setIsRefreshingOffers] = useState(true)

  const [areAllOffersSelected, setAreAllOffersSelected] = useState(false)
  const [selectedOfferIds, setSelectedOfferIds] = useState<string[]>([])
  const [selectedAudience, setSelectedAudience] =
    useState<Audience>(urlAudience)
  const [isStatusFiltersVisible, setIsStatusFiltersVisible] = useState(false)

  const { isAdmin } = currentUser || {}
  const currentPageOffersSubset = offers.slice(
    (currentPageNumber - 1) * NUMBER_OF_OFFERS_PER_PAGE,
    currentPageNumber * NUMBER_OF_OFFERS_PER_PAGE
  )
  const hasOffers = currentPageOffersSubset.length > 0

  const userHasNoOffers =
    !isLoading && !hasOffers && !hasSearchFilters(urlSearchFilters)

  const hasDifferentFiltersFromLastSearch = useCallback(
    (
      searchFilters: TSearchFilters,
      filterNames: (keyof TSearchFilters)[] = Object.keys(
        searchFilters
      ) as (keyof TSearchFilters)[]
    ) => {
      const lastSearchFilters = {
        ...DEFAULT_SEARCH_FILTERS,
        ...urlSearchFilters,
      }
      return filterNames
        .map(
          filterName =>
            searchFilters[filterName] !== lastSearchFilters[filterName]
        )
        .includes(true)
    },
    [urlSearchFilters]
  )

  const actionLink =
    userHasNoOffers || isAdmin ? null : (
      <Link className="primary-button with-icon" to="/offre/creation">
        <AddOfferSvg />
        Créer une offre
      </Link>
    )

  const nbSelectedOffers = areAllOffersSelected
    ? offers.length
    : selectedOfferIds.length

  const clearSelectedOfferIds = useCallback(() => {
    setSelectedOfferIds([])
  }, [])

  const refreshOffers = useCallback(
    () => loadAndUpdateOffers(initialSearchFilters),
    [loadAndUpdateOffers, initialSearchFilters]
  )

  const toggleSelectAllCheckboxes = useCallback(() => {
    setAreAllOffersSelected(currentValue => !currentValue)
  }, [])

  const resetFilters = useCallback(() => {
    setOfferer(null)
    setSearchFilters({ ...DEFAULT_SEARCH_FILTERS })
  }, [setSearchFilters, setOfferer])

  const numberOfPages = Math.ceil(offers.length / NUMBER_OF_OFFERS_PER_PAGE)
  const pageCount = Math.min(numberOfPages, MAX_TOTAL_PAGES)

  useEffect(() => {
    if (isRefreshingOffers) {
      setSearchFilters(initialSearchFilters)
      loadAndUpdateOffers(initialSearchFilters)
    }
  }, [
    isRefreshingOffers,
    loadAndUpdateOffers,
    setSearchFilters,
    initialSearchFilters,
  ])

  const applyUrlFiltersAndRedirect = useCallback(
    (
      filters: TSearchFilters & {
        page?: number
        audience?: Audience
      },
      isRefreshing = true
    ) => {
      setIsRefreshingOffers(isRefreshing)
      redirectWithUrlFilters(filters)
    },
    [setIsRefreshingOffers, redirectWithUrlFilters]
  )

  const onSelectAudience = (selectedAudience: Audience) => {
    applyUrlFiltersAndRedirect({
      ...DEFAULT_SEARCH_FILTERS,
      audience: selectedAudience,
    })
  }

  const applyFilters = useCallback(() => {
    setIsStatusFiltersVisible(false)
    if (!hasDifferentFiltersFromLastSearch(searchFilters)) {
      refreshOffers()
    }
    applyUrlFiltersAndRedirect(searchFilters)
  }, [
    hasDifferentFiltersFromLastSearch,
    refreshOffers,
    searchFilters,
    applyUrlFiltersAndRedirect,
  ])

  const removeOfferer = useCallback(() => {
    setOfferer(null)
    const updatedFilters = {
      ...searchFilters,
      offererId: DEFAULT_SEARCH_FILTERS.offererId,
    }
    if (
      searchFilters.venueId === DEFAULT_SEARCH_FILTERS.venueId &&
      searchFilters.status !== DEFAULT_SEARCH_FILTERS.status
    ) {
      updatedFilters.status = DEFAULT_SEARCH_FILTERS.status
    }
    applyUrlFiltersAndRedirect(updatedFilters)
  }, [applyUrlFiltersAndRedirect, searchFilters, setOfferer])

  useEffect(() => {
    setSelectedAudience(urlAudience)
  }, [urlAudience])

  return (
    <div className="offers-page">
      <PageTitle title="Vos offres" />
      <Titles action={actionLink} title="Offres" />
      {separateIndividualAndCollectiveOffers && (
        <OfferListFilterTabs
          onSelectAudience={onSelectAudience}
          selectedAudience={selectedAudience}
        />
      )}
      <ActionsBarPortal isVisible={nbSelectedOffers > 0}>
        <ActionsBarContainer
          areAllOffersSelected={areAllOffersSelected}
          clearSelectedOfferIds={clearSelectedOfferIds}
          nbSelectedOffers={nbSelectedOffers}
          refreshOffers={refreshOffers}
          selectedOfferIds={selectedOfferIds}
          toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
        />
      </ActionsBarPortal>
      <SearchFilters
        applyFilters={applyFilters}
        audience={urlAudience}
        categories={categories}
        disableAllFilters={userHasNoOffers}
        offerer={offerer}
        removeOfferer={removeOfferer}
        resetFilters={resetFilters}
        selectedFilters={searchFilters}
        setSearchFilters={setSearchFilters}
        venues={venues}
      />
      {userHasNoOffers ? (
        <NoOffers />
      ) : (
        <OffersContainer
          applyFilters={applyFilters}
          applyUrlFiltersAndRedirect={applyUrlFiltersAndRedirect}
          areAllOffersSelected={areAllOffersSelected}
          audience={urlAudience}
          currentPageNumber={currentPageNumber}
          currentPageOffersSubset={currentPageOffersSubset}
          currentUser={currentUser}
          hasOffers={hasOffers}
          isLoading={isLoading}
          isStatusFiltersVisible={isStatusFiltersVisible}
          offersCount={offers.length}
          pageCount={pageCount}
          resetFilters={resetFilters}
          searchFilters={searchFilters}
          selectedOfferIds={selectedOfferIds}
          setIsStatusFiltersVisible={setIsStatusFiltersVisible}
          setSearchFilters={setSearchFilters}
          setSelectedOfferIds={setSelectedOfferIds}
          toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
          urlSearchFilters={urlSearchFilters}
        />
      )}
    </div>
  )
}

export default Offers
