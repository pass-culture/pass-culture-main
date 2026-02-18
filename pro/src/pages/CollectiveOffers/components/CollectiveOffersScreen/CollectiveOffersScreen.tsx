import { useRef, useState } from 'react'

import {
  CollectiveOfferDisplayedStatus,
  type CollectiveOfferResponseModel,
} from '@/apiClient/v1'
import {
  type CollectiveOffersSortingColumn,
  isCollectiveOfferBookable,
} from '@/commons/core/OfferEducational/types'
import {
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  DEFAULT_PAGE,
  MAX_OFFERS_TO_DISPLAY,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
} from '@/commons/core/Offers/constants'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { hasCollectiveSearchFilters } from '@/commons/core/Offers/utils/hasSearchFilters'
import { useAccessibleScroll } from '@/commons/hooks/useAccessibleScroll'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useColumnSorting } from '@/commons/hooks/useColumnSorting'
import { usePagination } from '@/commons/hooks/usePagination'
import { getOffersCountToDisplay } from '@/commons/utils/getOffersCountToDisplay'
import { isCollectiveOfferSelectable } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { sortCollectiveOffers } from '@/commons/utils/sortCollectiveOffers'
import { AccessibleScrollContainer } from '@/components/AccessibleScrollContainer/AccessibleScrollContainer'
import { CollectiveBudgetBanner } from '@/components/CollectiveBudgetInformation/CollectiveBudgetBanner'
import { getCollectiveOfferColumns } from '@/components/CollectiveOffersTable/CollectiveOfferColumns/CollectiveOfferColumns'
import { ExpirationCell } from '@/components/CollectiveOffersTable/CollectiveOfferColumns/ExpirationCell/ExpirationCell'
import { CollectiveOffersActionsBar } from '@/components/CollectiveOffersTable/CollectiveOffersActionsBar/CollectiveOffersActionsBar'
import { CollectiveOffersDownloadDrawer } from '@/components/CollectiveOffersTable/CollectiveOffersDownloadDrawer/CollectiveOffersDownloadDrawer'
import { useStoredFilterConfig } from '@/components/OffersTableSearch/utils'
import { Banner } from '@/design-system/Banner/Banner'
import strokeNoBooking from '@/icons/stroke-no-booking.svg'
import { Table, TableVariant } from '@/ui-kit/Table/Table'

import styles from './CollectiveOffersScreen.module.scss'
import { CollectiveOffersSearchFilters } from './CollectiveOffersSearchFilters/CollectiveOffersSearchFilters'

export type CollectiveOffersScreenProps = {
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
  offers: CollectiveOfferResponseModel[]
}

function isCollectiveOfferPublishedOrPreBooked(
  offer: CollectiveOfferResponseModel
) {
  return (
    offer.displayedStatus === CollectiveOfferDisplayedStatus.PUBLISHED ||
    offer.displayedStatus === CollectiveOfferDisplayedStatus.PREBOOKED
  )
}

export const CollectiveOffersScreen = ({
  currentPageNumber,
  isLoading,
  offererId,
  initialSearchFilters,
  redirectWithUrlFilters,
  urlSearchFilters,
  offers,
}: CollectiveOffersScreenProps): JSX.Element => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

  const { onApplyFilters, onResetFilters } = useStoredFilterConfig('collective')
  const [selectedOffers, setSelectedOffers] = useState<
    CollectiveOfferResponseModel[]
  >([])
  const [selectedOfferIds, setSelectedOfferIds] = useState<
    Set<string | number>
  >(new Set())
  const [selectedFilters, setSelectedFilters] = useState(initialSearchFilters)

  const searchButtonRef = useRef<HTMLButtonElement>(null)

  const currentPageOffersSubset = offers.slice(
    (currentPageNumber - 1) * NUMBER_OF_OFFERS_PER_PAGE,
    currentPageNumber * NUMBER_OF_OFFERS_PER_PAGE
  )

  const hasOffers = currentPageOffersSubset.length > 0
  const hasFilters = hasCollectiveSearchFilters({
    searchFilters: initialSearchFilters,
    defaultFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
    ignore: [
      'name',
      ...((withSwitchVenueFeature
        ? ['venueId']
        : []) satisfies (keyof CollectiveSearchFiltersParams)[]),
    ],
  })
  const hasFiltersOrNameSearch = hasFilters || !!initialSearchFilters.name

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

  const resetFilters = (resetName = true) => {
    onResetFilters(resetName)
    const newFilters = {
      ...DEFAULT_COLLECTIVE_SEARCH_FILTERS,
      ...(!resetName && { name: initialSearchFilters.name }),
    }
    setSelectedFilters(newFilters)
    applyUrlFiltersAndRedirect(newFilters)
  }

  const columns = getCollectiveOfferColumns(urlSearchFilters, true)

  const { contentWrapperRef, scrollToContentWrapper } = useAccessibleScroll({
    selector: '#content-wrapper',
  })

  return (
    <div>
      <div className={styles['collective-budget-banner-container']}>
        <CollectiveBudgetBanner />
      </div>
      <CollectiveOffersSearchFilters
        hasFilters={hasFilters}
        applyFilters={applyFilters}
        disableAllFilters={userHasNoOffers}
        offererId={offererId}
        resetFilters={() => resetFilters(false)}
        selectedFilters={selectedFilters}
        setSelectedFilters={setSelectedFilters}
        searchButtonRef={searchButtonRef}
      />
      <output aria-live="polite">
        {offers.length > MAX_OFFERS_TO_DISPLAY && (
          <div className={styles['offers-table-callout']}>
            <Banner
              title="Limite d'affichage atteinte"
              description={`${MAX_OFFERS_TO_DISPLAY} offres maximum sont affichées. Affinez vos filtres pour cibler votre recherche.`}
            />
          </div>
        )}
        {hasOffers && (
          <div className={styles['offers-table-title']}>
            <div>
              <h2 className={styles['offers-table-title-heading']}>
                Liste des offres
              </h2>
              <div>
                {getOffersCountToDisplay(offers.length)}{' '}
                {pluralizeFr(offers.length, 'offre', 'offres')}
              </div>
            </div>
            <CollectiveOffersDownloadDrawer
              isDisabled={userHasNoOffers}
              filters={selectedFilters}
            />
          </div>
        )}
      </output>
      <AccessibleScrollContainer
        containerRef={contentWrapperRef}
        liveMessage={`Page ${page} sur ${pageCount}`}
      >
        <Table
          columns={columns}
          data={currentPageItems}
          allData={sortedOffers}
          isLoading={isLoading}
          selectable={true}
          selectedIds={selectedOfferIds}
          onSelectionChange={(rows) => {
            setSelectedOffers(rows)
            setSelectedOfferIds(new Set(rows.map((r) => r.id)))
          }}
          isRowSelectable={(row: CollectiveOfferResponseModel) =>
            isCollectiveOfferSelectable(row)
          }
          variant={TableVariant.COLLAPSE}
          noResult={{
            message: 'Aucune offre trouvée pour votre recherche',
            resetMessage: 'Afficher toutes les offres',
            onFilterReset: resetFilters,
          }}
          noData={{
            hasNoData: userHasNoOffers,
            message: {
              icon: strokeNoBooking,
              title: 'Vous n’avez pas encore créé d’offre',
              subtitle: '',
            },
          }}
          pagination={{
            currentPage: page,
            pageCount: pageCount,
            onPageClick: (page) => {
              applyUrlFiltersAndRedirect({ ...urlSearchFilters, page })
              scrollToContentWrapper()
            },
          }}
          getFullRowContent={(offer: CollectiveOfferResponseModel) => {
            const hasExpirationRow =
              isCollectiveOfferBookable(offer) &&
              isCollectiveOfferPublishedOrPreBooked(offer) &&
              !!offer.stock?.bookingLimitDatetime
            return hasExpirationRow ? <ExpirationCell offer={offer} /> : null
          }}
        />
      </AccessibleScrollContainer>
      <output>
        {selectedOfferIds.size > 0 && (
          <CollectiveOffersActionsBar
            areTemplateOffers={false}
            areAllOffersSelected={areAllOffersSelected}
            clearSelectedOfferIds={clearSelectedOfferIds}
            selectedOffers={selectedOffers}
            searchButtonRef={searchButtonRef}
          />
        )}
      </output>
    </div>
  )
}
