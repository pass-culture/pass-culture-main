import { useState } from 'react'

import {
  CollectiveOfferResponseModel,
  GetOffererResponseModel,
  UserRole,
} from 'apiClient/v1'
import { CollectiveOffersSortingColumn } from 'commons/core/OfferEducational/types'
import {
  DEFAULT_PAGE,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
} from 'commons/core/Offers/constants'
import { useDefaultCollectiveSearchFilters } from 'commons/core/Offers/hooks/useDefaultCollectiveSearchFilters'
import { CollectiveSearchFiltersParams } from 'commons/core/Offers/types'
import { hasCollectiveSearchFilters } from 'commons/core/Offers/utils/hasSearchFilters'
import { SelectOption } from 'commons/custom_types/form'
import { useColumnSorting } from 'commons/hooks/useColumnSorting'
import { usePagination } from 'commons/hooks/usePagination'
import { isSameOffer } from 'commons/utils/isSameOffer'
import { sortCollectiveOffers } from 'commons/utils/sortCollectiveOffers'
import { CollectiveOffersActionsBar } from 'components/CollectiveOffersTable/CollectiveOffersActionsBar/CollectiveOffersActionsBar'
import { CollectiveOffersTable } from 'components/CollectiveOffersTable/CollectiveOffersTable'
import { NoData } from 'components/NoData/NoData'
import { Pagination } from 'ui-kit/Pagination/Pagination'

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

  const defaultCollectiveFilters = useDefaultCollectiveSearchFilters()

  const currentPageOffersSubset = offers.slice(
    (currentPageNumber - 1) * NUMBER_OF_OFFERS_PER_PAGE,
    currentPageNumber * NUMBER_OF_OFFERS_PER_PAGE
  )

  const hasOffers = currentPageOffersSubset.length > 0

  const userHasNoOffers =
    !isLoading &&
    !hasOffers &&
    !hasCollectiveSearchFilters(
      { ...urlSearchFilters, offererId: 'all' },
      { ...defaultCollectiveFilters, offererId: 'all' }
    )

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
      <CollectiveOffersSearchFilters
        applyFilters={applyFilters}
        categories={categories}
        disableAllFilters={userHasNoOffers}
        offerer={offerer}
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
            isAtLeastOneOfferChecked={selectedOffers.length >= 1}
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
