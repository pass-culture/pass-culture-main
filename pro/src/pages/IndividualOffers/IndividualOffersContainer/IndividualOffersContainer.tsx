import { useRef, useState } from 'react'

import { type ListOffersOfferResponseModel, OfferStatus } from '@/apiClient/v1'
import { useHeadlineOfferContext } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import {
  DEFAULT_PAGE,
  DEFAULT_SEARCH_FILTERS,
  MAX_OFFERS_TO_DISPLAY,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
} from '@/commons/core/Offers/constants'
import type { IndividualSearchFiltersParams } from '@/commons/core/Offers/types'
import { hasSearchFilters } from '@/commons/core/Offers/utils/hasSearchFilters'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import type { Audience } from '@/commons/core/shared/types'
import type { SelectOption } from '@/commons/custom_types/form'
import { useAccessibleScroll } from '@/commons/hooks/useAccessibleScroll'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { getOffersCountToDisplay } from '@/commons/utils/getOffersCountToDisplay'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { AccessibleScrollContainer } from '@/components/AccessibleScrollContainer/AccessibleScrollContainer'
import { useStoredFilterConfig } from '@/components/OffersTableSearch/utils'
import { Banner } from '@/design-system/Banner/Banner'
import strokeNoBooking from '@/icons/stroke-no-booking.svg'
import { Table, TableVariant } from '@/ui-kit/Table/Table'

import { HeadlineOffer } from './components/HeadlineOffer/HeadlineOffer'
import { getIndividualOfferColumns } from './components/IndividualOfferColumns/IndividualOfferColumns'
import { IndividualOffersActionsBar } from './components/IndividualOffersActionsBar/IndividualOffersActionsBar'
import { IndividualOffersSearchFilters } from './components/IndividualOffersSearchFilters/IndividualOffersSearchFilters'
import styles from './IndividualOffersContainer.module.scss'

export type IndividualOffersContainerProps = {
  currentPageNumber: number
  isLoading: boolean
  initialSearchFilters: IndividualSearchFiltersParams
  redirectWithSelectedFilters: (
    filters: Partial<IndividualSearchFiltersParams> & {
      page?: number
      audience?: Audience
    }
  ) => void
  offererAddresses: SelectOption[]
  categories?: SelectOption[]
  offers?: ListOffersOfferResponseModel[]
}

export const IndividualOffersContainer = ({
  currentPageNumber,
  isLoading,
  initialSearchFilters,
  redirectWithSelectedFilters,
  offererAddresses,
  categories,
  offers = [],
}: IndividualOffersContainerProps): JSX.Element => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

  const { onApplyFilters, onResetFilters } = useStoredFilterConfig('individual')
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

  const hasFilters = hasSearchFilters({
    searchFilters: initialSearchFilters,
    ignore: withSwitchVenueFeature ? ['nameOrIsbn', 'venueId'] : ['nameOrIsbn'],
  })
  const hasFiltersOrNameSearch = hasFilters || !!initialSearchFilters.nameOrIsbn

  const userHasNoOffers = !isLoading && !hasOffers && !hasFiltersOrNameSearch

  const areAllOffersSelected =
    selectedOfferIds.size > 0 && selectedOfferIds.size === offers.length

  function clearSelectedOffers() {
    setSelectedOfferIds(new Set())
  }

  const numberOfPages = Math.ceil(offers.length / NUMBER_OF_OFFERS_PER_PAGE)
  const pageCount = Math.min(numberOfPages, MAX_TOTAL_PAGES)

  const applySelectedFiltersAndRedirect = (
    filters: Partial<IndividualSearchFiltersParams> & { audience?: Audience }
  ) => {
    redirectWithSelectedFilters(filters)
  }

  const applyFilters = (filters: IndividualSearchFiltersParams) => {
    onApplyFilters(filters)
    applySelectedFiltersAndRedirect({ ...filters, page: DEFAULT_PAGE })
  }

  const resetFilters = (resetNameOrIsbn = true) => {
    onResetFilters(resetNameOrIsbn)
    const newFilters = {
      ...DEFAULT_SEARCH_FILTERS,
      ...(!resetNameOrIsbn && { nameOrIsbn: initialSearchFilters.nameOrIsbn }),
    }
    setSelectedFilters(newFilters)
    applySelectedFiltersAndRedirect(newFilters)
  }

  const selectedOfferList = offers.filter((offer) =>
    selectedOfferIds.has(offer.id)
  )

  const canDelete = selectedOfferList.some(
    (offer) => offer.status === OfferStatus.DRAFT
  )

  const canPublish = selectedOfferList.some(
    (offer) => offer.status === OfferStatus.INACTIVE
  )

  const canDeactivate = selectedOfferList.some(
    (offer) =>
      offer.status === OfferStatus.ACTIVE ||
      offer.status === OfferStatus.EXPIRED ||
      offer.status === OfferStatus.SOLD_OUT
  )

  const { headlineOffer, isHeadlineOfferAllowedForOfferer } =
    useHeadlineOfferContext()

  const columns = getIndividualOfferColumns(
    headlineOffer,
    isHeadlineOfferAllowedForOfferer
  )

  const { contentWrapperRef, scrollToContentWrapper } = useAccessibleScroll({
    selector: '#content-wrapper',
  })

  return (
    <div>
      <IndividualOffersSearchFilters
        hasFilters={hasFilters}
        applyFilters={applyFilters}
        categories={categories}
        disableAllFilters={userHasNoOffers}
        resetFilters={() => resetFilters(false)}
        selectedFilters={selectedFilters}
        setSelectedFilters={setSelectedFilters}
        offererAddresses={offererAddresses}
        searchButtonRef={searchButtonRef}
      />

      <HeadlineOffer />

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
              {getOffersCountToDisplay(offers.length)}{' '}
              {pluralizeFr(offers.length, 'offre', 'offres')}
            </div>
          </div>
        )}
      </output>
      <AccessibleScrollContainer
        containerRef={contentWrapperRef}
        liveMessage={`Page ${currentPageNumber} sur ${pageCount}`}
      >
        <Table
          columns={columns}
          data={currentPageOffersSubset}
          allData={offers}
          isLoading={isLoading}
          variant={TableVariant.COLLAPSE}
          selectable={true}
          selectedIds={selectedOfferIds}
          onSelectionChange={(offers) =>
            setSelectedOfferIds(new Set(offers.map((r) => r.id)))
          }
          isRowSelectable={(offer) => !isOfferDisabled(offer)}
          noResult={{
            message: 'Aucune offre trouvée pour votre recherche',
            resetMessage: 'Afficher toutes les offres',
            onFilterReset: () => resetFilters(true),
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
            currentPage: currentPageNumber,
            pageCount: pageCount,
            onPageClick: (page) => {
              applySelectedFiltersAndRedirect({ ...selectedFilters, page })
              scrollToContentWrapper()
            },
          }}
        />
      </AccessibleScrollContainer>

      <output>
        {selectedOfferIds.size > 0 && (
          <IndividualOffersActionsBar
            areAllOffersSelected={areAllOffersSelected}
            clearSelectedOffers={clearSelectedOffers}
            selectedOffers={selectedOfferList}
            canDelete={canDelete}
            canDeactivate={canDeactivate}
            canPublish={canPublish}
            searchButtonRef={searchButtonRef}
          />
        )}
      </output>
    </div>
  )
}
