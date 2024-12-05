import { ListOffersOfferResponseModel } from 'apiClient/v1'
import { MAX_OFFERS_TO_DISPLAY } from 'commons/core/Offers/constants'
import { SearchFiltersParams } from 'commons/core/Offers/types'
import { hasSearchFilters } from 'commons/core/Offers/utils/hasSearchFilters'
import { getOffersCountToDisplay } from 'commons/utils/getOffersCountToDisplay'
import { NoResults } from 'components/NoResults/NoResults'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
import { Pagination } from 'ui-kit/Pagination/Pagination'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { IndividualOffersTableBody } from './components/IndividualOffersTableBody/IndividualOffersTableBody'
import { IndividualOffersTableHead } from './components/IndividualOfferTableHead/IndividualOffersTableHead'
import styles from './IndividualOffersTable.module.scss'

type IndividualOffersTableProps = {
  applyUrlFiltersAndRedirect: (
    filters: SearchFiltersParams,
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
  urlSearchFilters: SearchFiltersParams
  isAtLeastOneOfferChecked: boolean
  isRestrictedAsAdmin?: boolean
  currentPageOffersSubset: ListOffersOfferResponseModel[]
  selectedOffers: ListOffersOfferResponseModel[]
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
  applyUrlFiltersAndRedirect,
  setSelectedOffer,
  toggleSelectAllCheckboxes,
  urlSearchFilters,
  isAtLeastOneOfferChecked,
  isRestrictedAsAdmin = false,
}: IndividualOffersTableProps) => {
  const onPreviousPageClick = () =>
    applyUrlFiltersAndRedirect(
      { ...urlSearchFilters, page: currentPageNumber - 1 },
      false
    )

  const onNextPageClick = () =>
    applyUrlFiltersAndRedirect(
      { ...urlSearchFilters, page: currentPageNumber + 1 },
      false
    )

  return (
    <div>
      <div role="status">
        {offersCount > MAX_OFFERS_TO_DISPLAY && (
          <Callout
            variant={CalloutVariant.INFO}
            className={styles['max-display-callout']}
          >
            L’affichage est limité à 500 offres. Modifiez les filtres pour
            affiner votre recherche.
          </Callout>
        )}
        {hasOffers && (
          <div className={styles['individual-table-title']}>
            <h2 id="individual-table-title" className={styles['individual-table-title-heading']}>
              Liste des offres
            </h2>
            <div>
              {`${getOffersCountToDisplay(offersCount)} ${
                offersCount <= 1 ? 'offre' : 'offres'
              }`}
            </div>
          </div>
        )}
      </div>
      {isLoading ? (
        <Spinner className={styles['loading-spinner']} />
      ) : (
        <>
          {hasOffers && (
            <table role="table" className={styles['individual-table']} aria-labelledby="individual-table-title">
              <IndividualOffersTableHead
                areAllOffersSelected={areAllOffersSelected}
                isAtLeastOneOfferChecked={isAtLeastOneOfferChecked}
                isRestrictedAsAdmin={isRestrictedAsAdmin}
                toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
              />
              <IndividualOffersTableBody
                offers={currentPageOffersSubset}
                selectOffer={setSelectedOffer}
                selectedOffers={selectedOffers}
                isRestrictedAsAdmin={isRestrictedAsAdmin}
              />
            </table>
          )}
          {hasOffers && (
            <div className={styles['offers-pagination']}>
              <Pagination
                currentPage={currentPageNumber}
                pageCount={pageCount}
                onPreviousPageClick={onPreviousPageClick}
                onNextPageClick={onNextPageClick}
              />
            </div>
          )}
          {!hasOffers && hasSearchFilters(urlSearchFilters) && (
            <NoResults resetFilters={resetFilters} />
          )}
        </>
      )}
    </div>
  )
}
