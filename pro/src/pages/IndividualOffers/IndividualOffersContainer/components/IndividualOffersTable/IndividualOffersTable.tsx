import { ListOffersOfferResponseModel } from 'apiClient/v1'
import { SearchFiltersParams } from 'commons/core/Offers/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { OffersTable } from 'components/OffersTable/OffersTable'
import { OffersTableHead } from 'components/OffersTable/OffersTableHead/OffersTableHead'
import { getCellsDefinition } from 'components/OffersTable/utils/cellDefinitions'
import { Pagination } from 'ui-kit/Pagination/Pagination'

import { IndividualOffersTableBody } from './components/IndividualOffersTableBody/IndividualOffersTableBody'

type IndividualOffersTableProps = {
  applySelectedFiltersAndRedirect: (
    filters: Partial<SearchFiltersParams>,
    isRefreshing: boolean
  ) => void
  areAllOffersSelected: boolean
  currentPageNumber: number
  hasOffers: boolean
  isLoading: boolean
  offersCount: number
  pageCount: number
  resetFilters: () => void
  setSelectedOffer: (offer: ListOffersOfferResponseModel) => void
  toggleSelectAllCheckboxes: () => void
  hasFiltersOrNameSearch: boolean
  isAtLeastOneOfferChecked: boolean
  currentPageOffersSubset: ListOffersOfferResponseModel[]
  selectedOffers: ListOffersOfferResponseModel[]
  selectedFilters: SearchFiltersParams
}

export const IndividualOffersTable = ({
  areAllOffersSelected,
  currentPageNumber,
  currentPageOffersSubset,
  hasOffers,
  isLoading,
  offersCount,
  pageCount,
  resetFilters,
  selectedOffers,
  applySelectedFiltersAndRedirect,
  setSelectedOffer,
  toggleSelectAllCheckboxes,
  hasFiltersOrNameSearch,
  isAtLeastOneOfferChecked,
  selectedFilters,
}: IndividualOffersTableProps) => {
  const isRefactoFutureOfferEnabled = useActiveFeature(
    'WIP_REFACTO_FUTURE_OFFER'
  )

  const onPreviousPageClick = () =>
    applySelectedFiltersAndRedirect(
      { ...selectedFilters, page: currentPageNumber - 1 },
      false
    )

  const onNextPageClick = () =>
    applySelectedFiltersAndRedirect(
      { ...selectedFilters, page: currentPageNumber + 1 },
      false
    )

  const pagination = (
    <Pagination
      currentPage={currentPageNumber}
      pageCount={pageCount}
      onPreviousPageClick={onPreviousPageClick}
      onNextPageClick={onNextPageClick}
    />
  )

  return (
    <OffersTable
      hasOffers={hasOffers}
      hasFiltersOrNameSearch={hasFiltersOrNameSearch}
      offersCount={offersCount}
      isLoading={isLoading}
      resetFilters={resetFilters}
      pagination={pagination}
      areAllOffersSelected={areAllOffersSelected}
      isAtLeastOneOfferChecked={isAtLeastOneOfferChecked}
      toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
    >
      <OffersTableHead
        columns={[
          getCellsDefinition().NAME,
          getCellsDefinition().ADDRESS,
          getCellsDefinition().STOCKS,
          getCellsDefinition(isRefactoFutureOfferEnabled).INDIVIDUAL_STATUS,
        ]}
      />
      <IndividualOffersTableBody
        offers={currentPageOffersSubset}
        selectOffer={setSelectedOffer}
        selectedOffers={selectedOffers}
      />
    </OffersTable>
  )
}
