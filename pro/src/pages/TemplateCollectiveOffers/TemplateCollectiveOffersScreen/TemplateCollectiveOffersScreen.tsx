import { useState } from 'react'

import type { CollectiveOfferTemplateResponseModel } from '@/apiClient/v1'
import type { CollectiveOffersSortingColumn } from '@/commons/core/OfferEducational/types'
import {
  DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
  DEFAULT_PAGE,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
} from '@/commons/core/Offers/constants'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { hasCollectiveSearchFilters } from '@/commons/core/Offers/utils/hasSearchFilters'
import { useColumnSorting } from '@/commons/hooks/useColumnSorting'
import { usePagination } from '@/commons/hooks/usePagination'
import { isCollectiveOfferSelectable } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { sortCollectiveOffers } from '@/commons/utils/sortCollectiveOffers'
import { CollectiveOffersActionsBar } from '@/components/CollectiveOffersTable/CollectiveOffersActionsBar/CollectiveOffersActionsBar'
import { CollectiveOffersTable } from '@/components/CollectiveOffersTable/CollectiveOffersTable'
import { NoData } from '@/components/NoData/NoData'
import { useStoredFilterConfig } from '@/components/OffersTable/OffersTableSearch/utils'
import { Pagination } from '@/ui-kit/Pagination/Pagination'

import styles from './TemplateCollectiveOffersScreen.module.scss'
import { TemplateOffersSearchFilters } from './TemplateOffersSearchFilters/TemplateOffersSearchFilters'

export type TemplateCollectiveOffersScreenProps = {
  currentPageNumber: number
  isLoading: boolean
  offererId: string | undefined
  initialSearchFilters: CollectiveSearchFiltersParams
  redirectWithUrlFilters: (
    filters: Partial<CollectiveSearchFiltersParams> & {
      page?: number
    }
  ) => void
  urlSearchFilters: Partial<CollectiveSearchFiltersParams>
  offers: CollectiveOfferTemplateResponseModel[]
}

export const TemplateCollectiveOffersScreen = ({
  currentPageNumber,
  isLoading,
  offererId,
  initialSearchFilters,
  redirectWithUrlFilters,
  urlSearchFilters,
  offers,
}: TemplateCollectiveOffersScreenProps): JSX.Element => {
  const { onApplyFilters, onResetFilters } = useStoredFilterConfig('template')
  const [selectedOffers, setSelectedOffers] = useState<
    CollectiveOfferTemplateResponseModel[]
  >([])
  const [selectedFilters, setSelectedFilters] = useState(initialSearchFilters)

  const currentPageOffersSubset = offers.slice(
    (currentPageNumber - 1) * NUMBER_OF_OFFERS_PER_PAGE,
    currentPageNumber * NUMBER_OF_OFFERS_PER_PAGE
  )

  const hasOffers = currentPageOffersSubset.length > 0
  const hasFilters = hasCollectiveSearchFilters({
    searchFilters: initialSearchFilters,
    defaultFilters: DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
    ignore: ['nameOrIsbn', 'collectiveOfferType'],
  })
  const hasFiltersOrNameSearch = hasFilters || !!initialSearchFilters.nameOrIsbn

  const userHasNoOffers = !isLoading && !hasOffers && !hasFiltersOrNameSearch

  const areAllOffersSelected =
    selectedOffers.length > 0 &&
    selectedOffers.length ===
      offers.filter((offer) => isCollectiveOfferSelectable(offer)).length

  function clearSelectedOfferIds() {
    setSelectedOffers([])
  }

  function toggleSelectAllCheckboxes() {
    setSelectedOffers(
      areAllOffersSelected
        ? []
        : offers.filter((offer) => isCollectiveOfferSelectable(offer))
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

  const { page, currentPageItems, setPage } =
    usePagination<CollectiveOfferTemplateResponseModel>(
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

  const resetFilters = (resetNameOrIsbn = true) => {
    onResetFilters(resetNameOrIsbn)
    const newFilters = {
      ...DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
      ...(!resetNameOrIsbn && { nameOrIsbn: initialSearchFilters.nameOrIsbn }),
    }
    setSelectedFilters(newFilters)
    applyUrlFiltersAndRedirect(newFilters)
  }

  function onSetSelectedOffer(offer: CollectiveOfferTemplateResponseModel) {
    const matchingOffer = selectedOffers.find(
      (selectedOffer) => offer.id === selectedOffer.id
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
      <TemplateOffersSearchFilters
        hasFilters={hasFilters}
        applyFilters={applyFilters}
        disableAllFilters={userHasNoOffers}
        offererId={offererId}
        resetFilters={() => resetFilters(false)}
        selectedFilters={selectedFilters}
        setSelectedFilters={setSelectedFilters}
      />

      {userHasNoOffers ? (
        <NoData page="offers" />
      ) : (
        <>
          <CollectiveOffersTable
            hasFiltersOrNameSearch={hasFiltersOrNameSearch}
            areAllOffersSelected={areAllOffersSelected}
            hasOffers={hasOffers}
            isLoading={isLoading}
            resetFilters={resetFilters}
            selectedOffers={selectedOffers}
            setSelectedOffer={onSetSelectedOffer}
            toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
            urlSearchFilters={urlSearchFilters}
            isAtLeastOneOfferChecked={selectedOffers.length > 1}
            offers={sortedOffers}
            onColumnHeaderClick={onColumnHeaderClick}
            currentSortingColumn={currentSortingColumn}
            currentSortingMode={currentSortingMode}
            currentPageItems={currentPageItems}
            isTemplateTable={true}
          />
          {hasOffers && (
            <div className={styles['offers-pagination']}>
              <Pagination
                currentPage={page}
                pageCount={pageCount}
                onPreviousPageClick={() => {
                  applyUrlFiltersAndRedirect({
                    ...urlSearchFilters,
                    offererId: offererId?.toString() ?? '',
                    page: page - 1,
                  })
                }}
                onNextPageClick={() => {
                  applyUrlFiltersAndRedirect({
                    ...urlSearchFilters,
                    offererId: offererId?.toString() ?? '',
                    page: page + 1,
                  })
                }}
              />
            </div>
          )}
          <nav aria-label="Actions sur les offres">
            {selectedOffers.length > 0 && (
              <CollectiveOffersActionsBar
                areTemplateOffers
                areAllOffersSelected={areAllOffersSelected}
                clearSelectedOfferIds={clearSelectedOfferIds}
                selectedOffers={selectedOffers}
              />
            )}
          </nav>
        </>
      )}
    </div>
  )
}
