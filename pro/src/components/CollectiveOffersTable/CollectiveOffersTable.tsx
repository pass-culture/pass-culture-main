import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { CollectiveOffersSortingColumn } from 'commons/core/OfferEducational/types'
import { CollectiveSearchFiltersParams } from 'commons/core/Offers/types'
import { SortingMode } from 'commons/hooks/useColumnSorting'
import { OffersTable } from 'components/OffersTable/OffersTable'
import {
  Columns,
  OffersTableHead,
} from 'components/OffersTable/OffersTableHead/OffersTableHead'
import { CELLS_DEFINITIONS } from 'components/OffersTable/utils/cellDefinitions'

import { CollectiveOffersTableBody } from './CollectiveOffersTableBody/CollectiveOffersTableBody'

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
    { ...CELLS_DEFINITIONS.INFO_ON_EXPIRATION, isVisuallyHidden: true },
    { ...CELLS_DEFINITIONS.THUMB, isVisuallyHidden: true },
    { ...CELLS_DEFINITIONS.NAME, isVisuallyHidden: true },
    {
      ...CELLS_DEFINITIONS.EVENT_DATE,
      sortableProps: {
        onColumnHeaderClick,
        currentSortingColumn,
        currentSortingMode,
      },
    },
    CELLS_DEFINITIONS.STRUCTURE,
    CELLS_DEFINITIONS.INSTITUTION,
    CELLS_DEFINITIONS.STATUS,
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
      <CollectiveOffersTableBody
        offers={currentPageItems}
        selectOffer={setSelectedOffer}
        selectedOffers={selectedOffers}
        urlSearchFilters={urlSearchFilters}
      />
    </OffersTable>
  )
}
