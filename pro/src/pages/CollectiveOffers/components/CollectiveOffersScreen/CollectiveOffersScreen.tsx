import { useRef, useState } from 'react'

import {
  CollectiveOfferResponseModel,
  GetOffererResponseModel,
} from 'apiClient/v1'
import { CollectiveOffersSortingColumn } from 'commons/core/OfferEducational/types'
import {
  DEFAULT_PAGE,
  MAX_OFFERS_TO_DISPLAY,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
} from 'commons/core/Offers/constants'
import { useDefaultCollectiveSearchFilters } from 'commons/core/Offers/hooks/useDefaultCollectiveSearchFilters'
import { CollectiveSearchFiltersParams } from 'commons/core/Offers/types'
import { hasCollectiveSearchFilters } from 'commons/core/Offers/utils/hasSearchFilters'
import { SelectOption } from 'commons/custom_types/form'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useColumnSorting } from 'commons/hooks/useColumnSorting'
import { usePagination } from 'commons/hooks/usePagination'
import { getOffersCountToDisplay } from 'commons/utils/getOffersCountToDisplay'
import { isCollectiveOfferSelectable } from 'commons/utils/isActionAllowedOnCollectiveOffer'
import { sortCollectiveOffers } from 'commons/utils/sortCollectiveOffers'
import { CollectiveBudgetCallout } from 'components/CollectiveBudgetInformation/CollectiveBudgetCallout'
import { createCollectiveOfferColumns } from 'components/CollectiveOffersTable/CollectiveOfferRow/createCollectiveOfferColumns'
import { CollectiveOffersActionsBar } from 'components/CollectiveOffersTable/CollectiveOffersActionsBar/CollectiveOffersActionsBar'
import { NoData } from 'components/NoData/NoData'
import { useStoredFilterConfig } from 'components/OffersTable/OffersTableSearch/utils'
import { Callout } from 'ui-kit/Callout/Callout'
import { Pagination } from 'ui-kit/Pagination/Pagination'
import { Table } from 'ui-kit/Table/Table'

import styles from './CollectiveOffersScreen.module.scss'
import { CollectiveOffersSearchFilters } from './CollectiveOffersSearchFilters/CollectiveOffersSearchFilters'

export type CollectiveOffersScreenProps = {
  currentPageNumber: number
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
  offers,
}: CollectiveOffersScreenProps): JSX.Element => {
  const { onApplyFilters, onResetFilters } = useStoredFilterConfig('collective')
  const [selectedFilters, setSelectedFilters] = useState(initialSearchFilters)
  const [selectedOffers, setSelectedOffers] = useState<
    CollectiveOfferResponseModel[]
  >([])
  const [selected, setSelected] = useState<Set<string | number>>(new Set())

  const searchButtonRef = useRef<HTMLButtonElement>(null)

  const defaultCollectiveFilters = useDefaultCollectiveSearchFilters()
  const isCollapsedMemorizedFiltersEnabled = useActiveFeature(
    'WIP_COLLAPSED_MEMORIZED_FILTERS'
  )

  const currentPageOffersSubset = offers.slice(
    (currentPageNumber - 1) * NUMBER_OF_OFFERS_PER_PAGE,
    currentPageNumber * NUMBER_OF_OFFERS_PER_PAGE
  )

  const hasOffers = currentPageOffersSubset.length > 0
  const hasFilters = hasCollectiveSearchFilters({
    searchFilters: initialSearchFilters,
    defaultFilters: defaultCollectiveFilters,
    ignore: ['nameOrIsbn'],
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

  const numberOfPages = Math.ceil(offers.length / NUMBER_OF_OFFERS_PER_PAGE)
  const pageCount = Math.min(numberOfPages, MAX_TOTAL_PAGES)

  const { currentSortingColumn, currentSortingMode } =
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
    applyUrlFiltersAndRedirect({ ...filters, page: DEFAULT_PAGE })
  }

  const resetFilters = (resetNameOrIsbn = true) => {
    onResetFilters(resetNameOrIsbn)
    const newFilters = {
      ...defaultCollectiveFilters,
      ...(!resetNameOrIsbn && { nameOrIsbn: initialSearchFilters.nameOrIsbn }),
    }
    applyUrlFiltersAndRedirect(newFilters)
    setSelectedFilters(newFilters)
  }

  const { columns, getExpandedContent, getRowLink } =
    createCollectiveOfferColumns({
      selectedIds: selected,
      toggleSelect: (offer) => {
        const next = new Set(selected)
        next.has(offer.id) ? next.delete(offer.id) : next.add(offer.id)
        setSelected(next)
      },
      urlSearchFilters,
    })

  return (
    <div>
      {offerer?.allowedOnAdage && (
        <CollectiveBudgetCallout variant="COLLECTIVE_TABLE" pageName="offers" />
      )}
      <CollectiveOffersSearchFilters
        hasFilters={hasFilters}
        applyFilters={applyFilters}
        disableAllFilters={userHasNoOffers}
        offerer={offerer}
        resetFilters={() => resetFilters(!isCollapsedMemorizedFiltersEnabled)}
        selectedFilters={selectedFilters}
        setSelectedFilters={setSelectedFilters}
        venues={venues}
        searchButtonRef={searchButtonRef}
      />
      {userHasNoOffers ? (
        <NoData page="offers" />
      ) : (
        <>
          <div role="status">
            {sortedOffers.length > MAX_OFFERS_TO_DISPLAY && (
              <Callout className={styles['offers-table-callout']}>
                L’affichage est limité à {MAX_OFFERS_TO_DISPLAY} offres.
                Modifiez les filtres pour affiner votre recherche.
              </Callout>
            )}
            {hasOffers && (
              <div className={styles['offers-table-title']}>
                <h2
                  id="offers-table-title"
                  className={styles['offers-table-title-heading']}
                >
                  Liste des offres
                </h2>
                <div>
                  {`${getOffersCountToDisplay(sortedOffers.length)} ${
                    sortedOffers.length <= 1 ? 'offre' : 'offres'
                  }`}
                </div>
              </div>
            )}
          </div>

          <Table
            data={currentPageItems}
            columns={columns}
            selectable={true}
            getExpandedContent={getExpandedContent}
            getRowLink={getRowLink}
            onSelectionChange={setSelectedOffers}
            hasFiltersOrNameSearch={hasFiltersOrNameSearch}
            hasOffers={hasOffers}
            resetFilters={() =>
              resetFilters(!isCollapsedMemorizedFiltersEnabled)
            }
            isRowSelectable={(row) => isCollectiveOfferSelectable(row)}
            isLoading={isLoading}
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
                searchButtonRef={searchButtonRef}
                resetFilters={resetFilters}
                userHasNoOffers={userHasNoOffers}
              />
            )}
          </div>
        </>
      )}
    </div>
  )
}
