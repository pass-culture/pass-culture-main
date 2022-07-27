import React, { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import ActionsBarPortal from 'components/layout/ActionsBarPortal/ActionsBarPortal'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'
import ActionsBar from 'components/pages/Offers/Offers/ActionsBar'
import OffersContainer from 'components/pages/Offers/Offers/Offers'
import {
  DEFAULT_SEARCH_FILTERS,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
  hasSearchFilters,
} from 'core/Offers'
import { Offer, Offerer, Option, TSearchFilters } from 'core/Offers/types'
import { Audience } from 'core/shared'
import { ReactComponent as AddOfferSvg } from 'icons/ico-plus.svg'
import { ReactComponent as LibraryIcon } from 'icons/library.svg'
import { ReactComponent as UserIcon } from 'icons/user.svg'
import NoOffers from 'new_components/NoData'
import Tabs from 'new_components/Tabs'

import SearchFilters from './SearchFilters'

export interface IOffersProps {
  currentPageNumber: number
  currentUser: { isAdmin: boolean }
  isLoading: boolean
  loadAndUpdateOffers: (filters: TSearchFilters) => Promise<void>
  offerer: Offerer | null
  offers: Offer[]
  setOfferer: (offerer: Offerer | null) => void
  initialSearchFilters: TSearchFilters
  audience: Audience
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
  initialSearchFilters,
  audience,
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

  const actionLink = isAdmin ? null : (
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

  const resetFilters = () => {
    setOfferer(null)
    setSearchFilters({ ...DEFAULT_SEARCH_FILTERS })
  }

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

  const applyFilters = useCallback(() => {
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

  return (
    <div className="offers-page">
      <PageTitle title="Vos offres" />
      <Titles action={actionLink} title="Offres" />
      <Tabs
        selectedKey={audience}
        tabs={[
          {
            label: 'Offres individuelles',
            url: '/offres',
            key: 'individual',
            Icon: UserIcon,
          },
          {
            label: 'Offres collectives',
            url: '/offres/collectives',
            key: 'collective',
            Icon: LibraryIcon,
          },
        ]}
        withQueryParams
      />
      <ActionsBarPortal isVisible={nbSelectedOffers > 0}>
        <ActionsBar
          areAllOffersSelected={areAllOffersSelected}
          clearSelectedOfferIds={clearSelectedOfferIds}
          nbSelectedOffers={nbSelectedOffers}
          refreshOffers={refreshOffers}
          selectedOfferIds={selectedOfferIds}
          toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
          audience={audience}
        />
      </ActionsBarPortal>
      <SearchFilters
        applyFilters={applyFilters}
        audience={audience}
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
        <NoOffers audience={audience} page="offers" />
      ) : (
        <OffersContainer
          applyFilters={applyFilters}
          applyUrlFiltersAndRedirect={applyUrlFiltersAndRedirect}
          areAllOffersSelected={areAllOffersSelected}
          audience={audience}
          currentPageNumber={currentPageNumber}
          currentPageOffersSubset={currentPageOffersSubset}
          currentUser={currentUser}
          hasOffers={hasOffers}
          isLoading={isLoading}
          offersCount={offers.length}
          pageCount={pageCount}
          resetFilters={resetFilters}
          searchFilters={searchFilters}
          selectedOfferIds={selectedOfferIds}
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
