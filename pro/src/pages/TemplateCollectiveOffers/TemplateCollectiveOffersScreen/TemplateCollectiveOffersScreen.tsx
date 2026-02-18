import { useState } from 'react'

import type { CollectiveOfferTemplateResponseModel } from '@/apiClient/v1'
import type { CollectiveOffersSortingColumn } from '@/commons/core/OfferEducational/types'
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
import { sortCollectiveOffers } from '@/commons/utils/sortCollectiveOffers'
import { AccessibleScrollContainer } from '@/components/AccessibleScrollContainer/AccessibleScrollContainer'
import { getCollectiveOfferColumns } from '@/components/CollectiveOffersTable/CollectiveOfferColumns/CollectiveOfferColumns'
import { CollectiveOffersActionsBar } from '@/components/CollectiveOffersTable/CollectiveOffersActionsBar/CollectiveOffersActionsBar'
import { useStoredFilterConfig } from '@/components/OffersTableSearch/utils'
import { Banner } from '@/design-system/Banner/Banner'
import strokeNoBooking from '@/icons/stroke-no-booking.svg'
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
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

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

  const resetFilters = (resetName = true) => {
    onResetFilters(resetName)
    const newFilters = {
      ...DEFAULT_COLLECTIVE_SEARCH_FILTERS,
      ...(!resetName && { name: initialSearchFilters.name }),
    }
    setSelectedFilters(newFilters)
    applyUrlFiltersAndRedirect(newFilters)
  }

  const columns = getCollectiveOfferColumns(urlSearchFilters)

  const { contentWrapperRef, scrollToContentWrapper } = useAccessibleScroll({
    selector: '#content-wrapper',
  })

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
          <div className={styles['offers-table-callout']}>
            <Banner
              title="Limite d'affichage atteinte"
              description={`${MAX_OFFERS_TO_DISPLAY} offres maximum sont affichées. Affinez vos filtres pour cibler votre recherche.`}
            />
          </div>
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
          isRowSelectable={(row: CollectiveOfferTemplateResponseModel) =>
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
              applyUrlFiltersAndRedirect({
                ...urlSearchFilters,
                offererId: offererId?.toString() ?? '',
                page,
              })
              scrollToContentWrapper()
            },
          }}
        />
      </AccessibleScrollContainer>
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
