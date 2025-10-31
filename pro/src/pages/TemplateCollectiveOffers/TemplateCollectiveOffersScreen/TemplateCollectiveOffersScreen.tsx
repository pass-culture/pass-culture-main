import { useState } from 'react'

import type { CollectiveOfferTemplateResponseModel } from '@/apiClient/v1'
import type { CollectiveOffersSortingColumn } from '@/commons/core/OfferEducational/types'
import {
  DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
  DEFAULT_PAGE,
  MAX_OFFERS_TO_DISPLAY,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
} from '@/commons/core/Offers/constants'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { hasCollectiveSearchFilters } from '@/commons/core/Offers/utils/hasSearchFilters'
import { useColumnSorting } from '@/commons/hooks/useColumnSorting'
import { usePagination } from '@/commons/hooks/usePagination'
import { getOffersCountToDisplay } from '@/commons/utils/getOffersCountToDisplay'
import { isCollectiveOfferSelectable } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { sortCollectiveOffers } from '@/commons/utils/sortCollectiveOffers'
import { getCollectiveOfferColumns } from '@/components/CollectiveOffersTable/CollectiveOfferColumns/CollectiveOfferColumns'
import { CollectiveOffersActionsBar } from '@/components/CollectiveOffersTable/CollectiveOffersActionsBar/CollectiveOffersActionsBar'
import { useStoredFilterConfig } from '@/components/OffersTable/OffersTableSearch/utils'
import strokeNoBooking from '@/icons/stroke-no-booking.svg'
import { Callout } from '@/ui-kit/Callout/Callout'
import { Pagination } from '@/ui-kit/Pagination/Pagination'
import { Table, TableVariant } from '@/ui-kit/Table/Table'

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
  const [selectedOfferIds, setSelectedOfferIds] = useState<
    Set<string | number>
  >(new Set())
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
    selectedOfferIds.size > 0 &&
    selectedOfferIds.size ===
      offers.filter((offer) => isCollectiveOfferSelectable(offer)).length

  function clearSelectedOfferIds() {
    setSelectedOfferIds(new Set())
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

  const columns = getCollectiveOfferColumns(urlSearchFilters)

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

      <output aria-live="polite">
        {offers.length > MAX_OFFERS_TO_DISPLAY && (
          <Callout className={styles['offers-table-callout']}>
            L’affichage est limité à {MAX_OFFERS_TO_DISPLAY} offres. Modifiez
            les filtres pour affiner votre recherche.
          </Callout>
        )}
        {hasOffers && (
          <div className={styles['offers-table-title']}>
            <h2 className={styles['offers-table-title-heading']}>
              Liste des offres
            </h2>
            <div>
              {`${getOffersCountToDisplay(offers.length)} ${
                offers.length <= 1 ? 'offre' : 'offres'
              }`}
            </div>
          </div>
        )}
      </output>
      <Table
        columns={columns}
        data={currentPageItems}
        isLoading={isLoading}
        selectable={true}
        selectedIds={selectedOfferIds}
        onSelectionChange={(rows) => {
          setSelectedOffers(rows)
          setSelectedOfferIds(new Set(rows.map((r) => r.id)))
        }}
        isRowSelectable={(row: CollectiveOfferTemplateResponseModel) =>
          isCollectiveOfferSelectable(row)
        }
        variant={TableVariant.COLLAPSE}
        noResult={{
          message: 'Aucune offre trouvée pour votre recherche',
          resetMessage: 'Afficher toutes les offres',
          onFilterReset: () => resetFilters(false),
        }}
        noData={{
          hasNoData: userHasNoOffers,
          message: {
            icon: strokeNoBooking,
            title: 'Vous n’avez pas encore créé d’offre',
            subtitle: '',
          },
        }}
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

      <output>
        {selectedOfferIds.size > 0 && (
          <CollectiveOffersActionsBar
            areTemplateOffers
            areAllOffersSelected={areAllOffersSelected}
            clearSelectedOfferIds={clearSelectedOfferIds}
            selectedOffers={selectedOffers}
          />
        )}
      </output>
    </div>
  )
}
