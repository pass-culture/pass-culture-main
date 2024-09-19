import { useState } from 'react'

import {
  CollectiveOfferResponseModel,
  GetOffererResponseModel,
  UserRole,
} from 'apiClient/v1'
import { NoData } from 'components/NoData/NoData'
import {
  DEFAULT_COLLECTIVE_BOOKABLE_SEARCH_FILTERS,
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  DEFAULT_PAGE,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
} from 'core/Offers/constants'
import { CollectiveSearchFiltersParams } from 'core/Offers/types'
import { hasCollectiveSearchFilters } from 'core/Offers/utils/hasSearchFilters'
import { SelectOption } from 'custom_types/form'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useColumnSorting } from 'hooks/useColumnSorting'
import { usePagination } from 'hooks/usePagination'
import { CollectiveOffersActionsBar } from 'pages/Offers/OffersTable/CollectiveOffersTable/CollectiveOffersActionsBar/CollectiveOffersActionsBar'
import { CollectiveOffersTable } from 'pages/Offers/OffersTable/CollectiveOffersTable/CollectiveOffersTable'
import { isSameOffer } from 'pages/Offers/utils/isSameOffer'
import { Pagination } from 'ui-kit/Pagination/Pagination'
import { sortCollectiveOffers } from 'utils/sortCollectiveOffers'

import styles from './CollectiveOffersScreen.module.scss'
import { CollectiveOffersSearchFilters } from './CollectiveOffersSearchFilters/CollectiveOffersSearchFilters'

export type CollectiveOffersScreenProps = {
  currentPageNumber: number
  currentUser: {
    roles: Array<UserRole>
    isAdmin: boolean
  }
  isLoading: boolean
  offerer: GetOffererResponseModel | null
  initialSearchFilters: CollectiveSearchFiltersParams
  redirectWithUrlFilters: (
    filters: CollectiveSearchFiltersParams & {
      page?: number
    }
  ) => void
  urlSearchFilters: CollectiveSearchFiltersParams
  venues: SelectOption[]
  categories?: SelectOption[]
  isRestrictedAsAdmin?: boolean
  offers: CollectiveOfferResponseModel[]
}

export enum CollectiveOffersSortingColumn {
  EVENT_DATE = 'EVENT_DATE',
}

export const CollectiveOffersScreen = ({
  currentPageNumber,
  isLoading,
  offerer,
  initialSearchFilters,
  redirectWithUrlFilters,
  urlSearchFilters,
  venues,
  categories,
  isRestrictedAsAdmin,
  offers,
}: CollectiveOffersScreenProps): JSX.Element => {
  const [selectedOffers, setSelectedOffers] = useState<
    CollectiveOfferResponseModel[]
  >([])
  const [selectedFilters, setSelectedFilters] = useState(initialSearchFilters)

  const isNewOffersAndBookingsActive = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE'
  )

  const defaultCollectiveFilters = isNewOffersAndBookingsActive
    ? DEFAULT_COLLECTIVE_BOOKABLE_SEARCH_FILTERS
    : DEFAULT_COLLECTIVE_SEARCH_FILTERS

  const currentPageOffersSubset = offers.slice(
    (currentPageNumber - 1) * NUMBER_OF_OFFERS_PER_PAGE,
    currentPageNumber * NUMBER_OF_OFFERS_PER_PAGE
  )

  const hasOffers = currentPageOffersSubset.length > 0

  const userHasNoOffers =
    !isLoading &&
    !hasOffers &&
    !hasCollectiveSearchFilters(urlSearchFilters, defaultCollectiveFilters)

  const areAllOffersSelected =
    selectedOffers.length > 0 &&
    selectedOffers.length === offers.filter((offer) => offer.isEditable).length

  function clearSelectedOfferIds() {
    setSelectedOffers([])
  }

  function toggleSelectAllCheckboxes() {
    setSelectedOffers(
      areAllOffersSelected ? [] : offers.filter((offer) => offer.isEditable)
    )
  }

  const resetFilters = () => {
    setSelectedFilters(defaultCollectiveFilters)
    applyUrlFiltersAndRedirect(defaultCollectiveFilters)
  }

  const numberOfPages = Math.ceil(offers.length / NUMBER_OF_OFFERS_PER_PAGE)
  const pageCount = Math.min(numberOfPages, MAX_TOTAL_PAGES)

  const { currentSortingColumn, currentSortingMode, onColumnHeaderClick } =
    useColumnSorting<CollectiveOffersSortingColumn>()

  const sortedOffers = sortCollectiveOffers(
    offers,
    currentSortingColumn,
    currentSortingMode
  )

  const { page, currentPageItems, setPage } = usePagination(
    sortedOffers,
    NUMBER_OF_OFFERS_PER_PAGE,
    urlSearchFilters.page
  )

  const applyUrlFiltersAndRedirect = (
    filters: CollectiveSearchFiltersParams
  ) => {
    setPage(filters.page ?? 1)
    redirectWithUrlFilters(filters)
  }

  const applyFilters = (filters: CollectiveSearchFiltersParams) => {
    applyUrlFiltersAndRedirect({ ...filters, page: DEFAULT_PAGE })
  }

  const removeOfferer = () => {
    const updatedFilters = {
      ...initialSearchFilters,
      offererId: defaultCollectiveFilters.offererId,
    }
    if (
      initialSearchFilters.venueId === defaultCollectiveFilters.venueId &&
      initialSearchFilters.status !== defaultCollectiveFilters.status
    ) {
      updatedFilters.status = defaultCollectiveFilters.status
    }
    applyUrlFiltersAndRedirect(updatedFilters)
  }

  function onSetSelectedOffer(offer: CollectiveOfferResponseModel) {
    const matchingOffer = selectedOffers.find((selectedOffer) =>
      isSameOffer(offer, selectedOffer)
    )

    if (matchingOffer) {
      setSelectedOffers((offers) =>
        offers.filter((collectiveOffer) => collectiveOffer !== matchingOffer)
      )
    } else {
      setSelectedOffers((selectedOffers) => {
        return [...selectedOffers, offer]
      })
    }
  }

  return (
    <div>
      <h1 className={styles['title']}>Offres collectives</h1>
      <CollectiveOffersSearchFilters
        applyFilters={applyFilters}
        categories={categories}
        disableAllFilters={userHasNoOffers}
        offerer={offerer}
        removeOfferer={removeOfferer}
        resetFilters={resetFilters}
        selectedFilters={selectedFilters}
        setSelectedFilters={setSelectedFilters}
        venues={venues}
        isRestrictedAsAdmin={isRestrictedAsAdmin}
      />
      {userHasNoOffers ? (
        <NoData page="offers" />
      ) : (
        <>
          <CollectiveOffersTable
            areAllOffersSelected={areAllOffersSelected}
            hasOffers={hasOffers}
            isLoading={isLoading}
            resetFilters={resetFilters}
            selectedOffers={selectedOffers}
            setSelectedOffer={onSetSelectedOffer}
            toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
            urlSearchFilters={urlSearchFilters}
            isAtLeastOneOfferChecked={selectedOffers.length > 1}
            isRestrictedAsAdmin={isRestrictedAsAdmin}
            offers={sortedOffers}
            onColumnHeaderClick={onColumnHeaderClick}
            currentSortingColumn={currentSortingColumn}
            currentSortingMode={currentSortingMode}
            currentPageItems={currentPageItems}
          />
          {hasOffers && (
            <div className={styles['offers-pagination']}>
              <Pagination
                currentPage={page}
                pageCount={pageCount}
                onPreviousPageClick={() => {
                  applyUrlFiltersAndRedirect({
                    ...urlSearchFilters,
                    page: page - 1,
                  })
                }}
                onNextPageClick={() => {
                  applyUrlFiltersAndRedirect({
                    ...urlSearchFilters,
                    page: page + 1,
                  })
                }}
              />
            </div>
          )}
          <div role="status">
            {selectedOffers.length > 0 && (
              <CollectiveOffersActionsBar
                areTemplateOffers={false}
                areAllOffersSelected={areAllOffersSelected}
                clearSelectedOfferIds={clearSelectedOfferIds}
                selectedOffers={selectedOffers}
              />
            )}
          </div>
        </>
      )}
    </div>
  )
}
