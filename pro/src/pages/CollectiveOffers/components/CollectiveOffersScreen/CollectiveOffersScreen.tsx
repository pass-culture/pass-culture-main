import { useRef, useState } from 'react'

import type {
  CollectiveOfferResponseModel,
  GetOffererResponseModel,
} from '@/apiClient/v1'
import type { CollectiveOffersSortingColumn } from '@/commons/core/OfferEducational/types'
import {
  DEFAULT_PAGE,
  MAX_OFFERS_TO_DISPLAY,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
} from '@/commons/core/Offers/constants'
import { useDefaultCollectiveSearchFilters } from '@/commons/core/Offers/hooks/useDefaultCollectiveSearchFilters'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { hasCollectiveSearchFilters } from '@/commons/core/Offers/utils/hasSearchFilters'
import type { SelectOption } from '@/commons/custom_types/form'
import { useColumnSorting } from '@/commons/hooks/useColumnSorting'
import { usePagination } from '@/commons/hooks/usePagination'
import { getOffersCountToDisplay } from '@/commons/utils/getOffersCountToDisplay'
import { isCollectiveOfferSelectable } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { sortCollectiveOffers } from '@/commons/utils/sortCollectiveOffers'
import { CollectiveBudgetCallout } from '@/components/CollectiveBudgetInformation/CollectiveBudgetCallout'
import { getCollectiveOfferColumns } from '@/components/CollectiveOffersTable/CollectiveOfferRow/CollectiveOfferColumns'
import { ExpirationCell } from '@/components/CollectiveOffersTable/CollectiveOfferRow/ExpirationCell/ExpirationCell'
import { CollectiveOffersActionsBar } from '@/components/CollectiveOffersTable/CollectiveOffersActionsBar/CollectiveOffersActionsBar'
import { useStoredFilterConfig } from '@/components/OffersTableSearch/utils'
import strokeNoBooking from '@/icons/stroke-no-booking.svg'
import { Callout } from '@/ui-kit/Callout/Callout'
import { Pagination } from '@/ui-kit/Pagination/Pagination'
import { Table, TableVariant } from '@/ui-kit/Table/Table'

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
  const [selectedOffers, setSelectedOffers] = useState<
    CollectiveOfferResponseModel[]
  >([])
  const [selectedOfferIds, setSelectedOfferIds] = useState<
    Set<string | number>
  >(new Set())
  const [selectedFilters, setSelectedFilters] = useState(initialSearchFilters)

  const searchButtonRef = useRef<HTMLButtonElement>(null)

  const defaultCollectiveFilters = useDefaultCollectiveSearchFilters()

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
    selectedOfferIds.size > 0 &&
    selectedOfferIds.size ===
      offers.filter((offer) => isCollectiveOfferSelectable(offer)).length

  function clearSelectedOffers() {
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

  const columns = getCollectiveOfferColumns(urlSearchFilters)

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
        resetFilters={() => resetFilters(false)}
        selectedFilters={selectedFilters}
        setSelectedFilters={setSelectedFilters}
        venues={venues}
        searchButtonRef={searchButtonRef}
      />

      <div>
        {offers.length > MAX_OFFERS_TO_DISPLAY && (
          <Callout className={styles['offers-table-callout']}>
            L’affichage est limité à {MAX_OFFERS_TO_DISPLAY} offres. Modifiez
            les filtres pour affiner votre recherche.
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
              {`${getOffersCountToDisplay(offers.length)} ${
                offers.length <= 1 ? 'offre' : 'offres'
              }`}
            </div>
          </div>
        )}
      </div>

      <Table
        columns={columns}
        data={currentPageItems}
        isLoading={isLoading}
        variant={TableVariant.COLLAPSE}
        selectable={true}
        selectedIds={selectedOfferIds}
        onSelectionChange={(rows) => {
          setSelectedOffers(rows)
          setSelectedOfferIds(new Set(rows.map((r) => r.id)))
        }}
        isRowSelectable={(row: CollectiveOfferResponseModel) =>
          isCollectiveOfferSelectable(row)
        }
        getFullRowContent={(offer: CollectiveOfferResponseModel) => {
          return (
            <ExpirationCell
              offer={offer}
              bookingLimitDate={
                offer.stocks[0]?.bookingLimitDatetime ?? undefined
              }
            />
          )
        }}
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

      {selectedOfferIds.size > 0 && (
        <CollectiveOffersActionsBar
          areTemplateOffers={false}
          areAllOffersSelected={areAllOffersSelected}
          clearSelectedOfferIds={clearSelectedOffers}
          selectedOffers={selectedOffers}
          searchButtonRef={searchButtonRef}
        />
      )}
    </div>
  )
}
