import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { CollectiveOffersSortingColumn } from 'commons/core/OfferEducational/types'
import { CollectiveSearchFiltersParams } from 'commons/core/Offers/types'
import { SortingMode } from 'commons/hooks/useColumnSorting'
import { isSameOffer } from 'commons/utils/isSameOffer'
import { OffersTable } from 'components/OffersTable/OffersTable'
import {
  Columns,
  OffersTableHead,
} from 'components/OffersTable/OffersTableHead/OffersTableHead'
import { getCellsDefinition } from 'components/OffersTable/utils/cellDefinitions'

import { CollectiveOfferRow } from './CollectiveOfferRow/CollectiveOfferRow'
import styles from './CollectiveOffersTable.module.scss'

type CollectiveOffersTableProps = {
  hasFiltersOrNameSearch: boolean
  areAllOffersSelected: boolean
  hasOffers: boolean
  isLoading: boolean
  resetFilters: () => void
  setSelectedOffer: (offer: CollectiveOfferResponseModel) => void
  toggleSelectAllCheckboxes: () => void
  urlSearchFilters: Partial<CollectiveSearchFiltersParams>
  isAtLeastOneOfferChecked: boolean
  selectedOffers: CollectiveOfferResponseModel[]
  offers: CollectiveOfferResponseModel[]
  onColumnHeaderClick: (
    headersName: CollectiveOffersSortingColumn
  ) => SortingMode
  currentSortingColumn: CollectiveOffersSortingColumn | null
  currentSortingMode: SortingMode
  currentPageItems: CollectiveOfferResponseModel[]
}

export const CollectiveOffersTable = ({
  hasFiltersOrNameSearch,
  areAllOffersSelected,
  hasOffers,
  isLoading,
  resetFilters,
  selectedOffers,
  setSelectedOffer,
  toggleSelectAllCheckboxes,
  urlSearchFilters,
  isAtLeastOneOfferChecked,
  offers,
  onColumnHeaderClick,
  currentSortingColumn,
  currentSortingMode,
  currentPageItems,
}: CollectiveOffersTableProps) => {
  const columns: Columns[] = [
    { ...getCellsDefinition().INFO_ON_EXPIRATION, isVisuallyHidden: true },
    { ...getCellsDefinition().NAME, isVisuallyHidden: false },
    {
      ...getCellsDefinition().EVENT_DATE,
      sortableProps: {
        onColumnHeaderClick,
        currentSortingColumn,
        currentSortingMode,
      },
    },
    getCellsDefinition().STRUCTURE,
    getCellsDefinition().INSTITUTION,
    getCellsDefinition().COLLECTIVE_STATUS,
  ]

  return (
    <OffersTable
      hasOffers={hasOffers}
      hasFiltersOrNameSearch={hasFiltersOrNameSearch}
      offersCount={offers.length}
      isLoading={isLoading}
      resetFilters={resetFilters}
      areAllOffersSelected={areAllOffersSelected}
      isAtLeastOneOfferChecked={isAtLeastOneOfferChecked}
      toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
    >
      <OffersTableHead columns={columns} />

      <tbody className={styles['collective-tbody']}>
        {currentPageItems.map((offer, index) => {
          const isSelected = selectedOffers.some((selectedOffer) =>
            isSameOffer(selectedOffer, offer)
          )

          return (
            <CollectiveOfferRow
              isSelected={isSelected}
              key={`${offer.isShowcase ? 'T-' : ''}${offer.id}`}
              offer={offer}
              selectOffer={setSelectedOffer}
              urlSearchFilters={urlSearchFilters}
              isFirstRow={index === 0}
            />
          )
        })}
      </tbody>
    </OffersTable>
  )
}
