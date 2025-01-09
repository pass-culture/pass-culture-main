import { useState, useEffect } from 'react'

import {
  CollectiveOfferResponseModel,
  GetOffererResponseModel,
  UserRole,
} from 'apiClient/v1'
import { CollectiveOffersSortingColumn } from 'commons/core/OfferEducational/types'
import {
  DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
  DEFAULT_PAGE,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
} from 'commons/core/Offers/constants'
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
import { useStoredFilterConfig } from 'components/OffersTable/OffersTableSearch/utils'
import { Pagination } from 'ui-kit/Pagination/Pagination'

import styles from './TemplateCollectiveOffersScreen.module.scss'
import { TemplateOffersSearchFilters } from './TemplateOffersSearchFilters/TemplateOffersSearchFilters'

export type TemplateCollectiveOffersScreenProps = {
  currentPageNumber: number
  currentUser: {
    roles: Array<UserRole>
    isAdmin: boolean
  }
  isLoading: boolean
  offerer: GetOffererResponseModel | null
  initialSearchFilters: CollectiveSearchFiltersParams
  redirectWithUrlFilters: (
    filters: Partial<CollectiveSearchFiltersParams> & {
      page?: number
    }
  ) => void
  urlSearchFilters: Partial<CollectiveSearchFiltersParams>
  venues: SelectOption[]
  categories?: SelectOption[]
  isRestrictedAsAdmin?: boolean
  offers: CollectiveOfferResponseModel[]
}

export const TemplateCollectiveOffersScreen = ({
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
}: TemplateCollectiveOffersScreenProps): JSX.Element => {
  const {
    onApplyFilters,
    onResetFilters,
  } = useStoredFilterConfig('template')
  const [selectedOffers, setSelectedOffers] = useState<
    CollectiveOfferResponseModel[]
  >([])
  const [selectedFilters, setSelectedFilters] = useState(initialSearchFilters)

  useEffect(() => {
    setSelectedFilters(initialSearchFilters)
  }, [initialSearchFilters])

  const currentPageOffersSubset = offers.slice(
    (currentPageNumber - 1) * NUMBER_OF_OFFERS_PER_PAGE,
    currentPageNumber * NUMBER_OF_OFFERS_PER_PAGE
  )

  const hasOffers = currentPageOffersSubset.length > 0

  const userHasNoOffers =
    !isLoading &&
    !hasOffers &&
    !hasCollectiveSearchFilters(
      urlSearchFilters,
      DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS
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
    filters: Partial<CollectiveSearchFiltersParams>
  ) => {
    setPage(filters.page ?? 1)
    redirectWithUrlFilters(filters)
  }

  const applyFilters = (filters: CollectiveSearchFiltersParams) => {
    onApplyFilters(filters)
    applyUrlFiltersAndRedirect({
      ...filters,
      page: DEFAULT_PAGE,
    })
  }

  const resetFilters = () => {
    onResetFilters()
    applyUrlFiltersAndRedirect(DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS)
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

  const hasFilters = hasCollectiveSearchFilters(
    initialSearchFilters,
    DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS
  )

  return (
    <div>
      <h1 className={styles['title']}>Offres vitrines</h1>
      <TemplateOffersSearchFilters
        hasFilters={hasFilters}
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
            hasFilters={hasFilters}
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
                    offererId: offerer?.id.toString() ?? '',
                    page: page - 1,
                  })
                }}
                onNextPageClick={() => {
                  applyUrlFiltersAndRedirect({
                    ...urlSearchFilters,
                    offererId: offerer?.id.toString() ?? '',
                    page: page + 1,
                  })
                }}
              />
            </div>
          )}
          <div role="status">
            {selectedOffers.length > 0 && (
              <CollectiveOffersActionsBar
                areTemplateOffers
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
