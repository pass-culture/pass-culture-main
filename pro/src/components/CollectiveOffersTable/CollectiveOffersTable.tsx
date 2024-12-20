import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { CollectiveOffersSortingColumn } from 'commons/core/OfferEducational/types'
import { useDefaultCollectiveSearchFilters } from 'commons/core/Offers/hooks/useDefaultCollectiveSearchFilters'
import { CollectiveSearchFiltersParams } from 'commons/core/Offers/types'
import { hasCollectiveSearchFilters } from 'commons/core/Offers/utils/hasSearchFilters'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { SortingMode } from 'commons/hooks/useColumnSorting'
import { OffersTable } from 'components/OffersTable/OffersTable'
import { Columns, OffersTableHead } from 'components/OffersTable/OffersTableHead/OffersTableHead'
import { CELLS_DEFINITIONS } from 'components/OffersTable/utils/cellDefinitions'

import { CollectiveOffersTableBody } from './CollectiveOffersTableBody/CollectiveOffersTableBody'

type CollectiveOffersTableProps = {
  areAllOffersSelected: boolean
  hasOffers: boolean
  isLoading: boolean
  resetFilters: () => void
  setSelectedOffer: (offer: CollectiveOfferResponseModel) => void
  toggleSelectAllCheckboxes: () => void
  urlSearchFilters: CollectiveSearchFiltersParams
  isAtLeastOneOfferChecked: boolean
  isRestrictedAsAdmin?: boolean
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
  areAllOffersSelected,
  hasOffers,
  isLoading,
  resetFilters,
  selectedOffers,
  setSelectedOffer,
  toggleSelectAllCheckboxes,
  urlSearchFilters,
  isAtLeastOneOfferChecked,
  isRestrictedAsAdmin = false,
  offers,
  onColumnHeaderClick,
  currentSortingColumn,
  currentSortingMode,
  currentPageItems,
}: CollectiveOffersTableProps) => {
  const defaultCollectiveFilters = useDefaultCollectiveSearchFilters()
  const isCollectiveOffersExpirationEnabled = useActiveFeature(
      'ENABLE_COLLECTIVE_OFFERS_EXPIRATION'
    )
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  type ConditionalColumn = Columns & { isDisplayed?: boolean }
  const conditionalColumns: ConditionalColumn[] = [
    { ...CELLS_DEFINITIONS.INFO_ON_EXPIRATION, isDisplayed: isCollectiveOffersExpirationEnabled },
    { ...CELLS_DEFINITIONS.THUMB, isVisuallyHidden: true },
    { ...CELLS_DEFINITIONS.NAME, isVisuallyHidden: true },
    { ...CELLS_DEFINITIONS.EVENT_DATE, sortableProps: {
      onColumnHeaderClick,
      currentSortingColumn,
      currentSortingMode,
    }, isDisplayed: isCollectiveOffersExpirationEnabled },
    (isOfferAddressEnabled ? CELLS_DEFINITIONS.STRUCTURE : CELLS_DEFINITIONS.VENUE),
    CELLS_DEFINITIONS.INSTITUTION,
    CELLS_DEFINITIONS.STATUS,
  ]
  const columns = conditionalColumns.reduce((acc: Columns[], curr) => {
    const { isDisplayed = true, ...rest} = curr
    if (isDisplayed) {
      acc.push(rest)
    }
  
    return acc
  }, [])

  return (
    <OffersTable
      hasOffers={hasOffers}
      hasFilters={hasCollectiveSearchFilters(
        urlSearchFilters,
        defaultCollectiveFilters
      )}
      offersCount={offers.length}
      isLoading={isLoading}
      resetFilters={resetFilters}
    >
      <OffersTableHead
        areAllOffersSelected={areAllOffersSelected}
        isAtLeastOneOfferChecked={isAtLeastOneOfferChecked}
        isRestrictedAsAdmin={isRestrictedAsAdmin}
        toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
        columns={columns}
      />
      <CollectiveOffersTableBody
        offers={currentPageItems}
        selectOffer={setSelectedOffer}
        selectedOffers={selectedOffers}
        urlSearchFilters={urlSearchFilters}
      />
    </OffersTable>
  )
}
