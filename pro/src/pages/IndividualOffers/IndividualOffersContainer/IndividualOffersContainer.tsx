import { useRef, useState } from 'react'

import { ListOffersOfferResponseModel, OfferStatus } from '@/apiClient/v1'
import { useHeadlineOfferContext } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import {
  DEFAULT_PAGE,
  DEFAULT_SEARCH_FILTERS,
  MAX_OFFERS_TO_DISPLAY,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
} from '@/commons/core/Offers/constants'
import { SearchFiltersParams } from '@/commons/core/Offers/types'
import { hasSearchFilters } from '@/commons/core/Offers/utils/hasSearchFilters'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import { Audience } from '@/commons/core/shared/types'
import { SelectOption } from '@/commons/custom_types/form'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { getOffersCountToDisplay } from '@/commons/utils/getOffersCountToDisplay'
import { useStoredFilterConfig } from '@/components/OffersTable/OffersTableSearch/utils'
import strokeNoBooking from '@/icons/stroke-no-booking.svg'
import { Callout } from '@/ui-kit/Callout/Callout'
import { Pagination } from '@/ui-kit/Pagination/Pagination'
import { Table, TableVariant } from '@/ui-kit/Table/Table'

import { HeadlineOffer } from './components/HeadlineOffer/HeadlineOffer'
import { getIndividualOfferColumns } from './components/IndividualOfferColumns/IndividualOfferColumns'
import { IndividualOffersActionsBar } from './components/IndividualOffersActionsBar/IndividualOffersActionsBar'
import { IndividualOffersSearchFilters } from './components/IndividualOffersSearchFilters/IndividualOffersSearchFilters'
import styles from './IndividualOffersContainer.module.scss'

export type IndividualOffersContainerProps = {
  currentPageNumber: number
  isLoading: boolean
  initialSearchFilters: SearchFiltersParams
  redirectWithSelectedFilters: (
    filters: Partial<SearchFiltersParams> & {
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
    ignore: ['nameOrIsbn'],
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
    filters: Partial<SearchFiltersParams> & { audience?: Audience }
  ) => {
    redirectWithSelectedFilters(filters)
  }

  const applyFilters = (filters: SearchFiltersParams) => {
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

  const onPreviousPageClick = () =>
    applySelectedFiltersAndRedirect({
      ...selectedFilters,
      page: currentPageNumber - 1,
    })

  const onNextPageClick = () =>
    applySelectedFiltersAndRedirect({
      ...selectedFilters,
      page: currentPageNumber + 1,
    })

  const isRefactoFutureOfferEnabled = useActiveFeature(
    'WIP_REFACTO_FUTURE_OFFER'
  )

  const { headlineOffer, isHeadlineOfferAllowedForOfferer } =
    useHeadlineOfferContext()

  const columns = getIndividualOfferColumns(
    isRefactoFutureOfferEnabled,
    headlineOffer,
    isHeadlineOfferAllowedForOfferer
  )

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
      <>
        <HeadlineOffer />

        <div role="status">
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
          data={currentPageOffersSubset}
          isLoading={isLoading}
          variant={TableVariant.COLLAPSE}
          selectable={true}
          selectedIds={selectedOfferIds}
          onSelectionChange={(rows) =>
            setSelectedOfferIds(new Set(rows.map((r) => r.id)))
          }
          isRowSelectable={(row: ListOffersOfferResponseModel) =>
            !isOfferDisabled(row.status)
          }
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

        <div className={styles['offers-table-pagination']}>
          <Pagination
            currentPage={currentPageNumber}
            pageCount={pageCount}
            onPreviousPageClick={onPreviousPageClick}
            onNextPageClick={onNextPageClick}
          />
        </div>

        <div role="status">
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
        </div>
      </>
    </div>
  )
}
