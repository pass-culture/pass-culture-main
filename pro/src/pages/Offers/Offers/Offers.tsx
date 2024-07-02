import {
  CollectiveOfferResponseModel,
  ListOffersOfferResponseModel,
} from 'apiClient/v1'
import { MAX_OFFERS_TO_DISPLAY } from 'core/Offers/constants'
import { SearchFiltersParams } from 'core/Offers/types'
import { hasSearchFilters } from 'core/Offers/utils/hasSearchFilters'
import { Audience } from 'core/shared/types'
import { getOffersCountToDisplay } from 'pages/Offers/domain/getOffersCountToDisplay'
import { NoResults } from 'screens/Offers/NoResults/NoResults'
import { Banner } from 'ui-kit/Banners/Banner/Banner'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { Pagination } from 'ui-kit/Pagination/Pagination'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import styles from './Offers.module.scss'
import { OffersTableBody } from './OffersTableBody/OffersTableBody'
import { OffersTableHead } from './OffersTableHead/OffersTableHead'

type OffersProps = {
  applyUrlFiltersAndRedirect: (
    filters: SearchFiltersParams,
    isRefreshing: boolean
  ) => void
  areAllOffersSelected: boolean
  audience: Audience
  currentPageNumber: number
  currentPageOffersSubset:
    | CollectiveOfferResponseModel[]
    | ListOffersOfferResponseModel[]
  currentUser: { isAdmin: boolean }
  hasOffers: boolean
  isLoading: boolean
  offersCount: number
  pageCount: number
  resetFilters: () => void
  selectedOffers:
    | CollectiveOfferResponseModel[]
    | ListOffersOfferResponseModel[]
  setSelectedOffer: (
    offer: ListOffersOfferResponseModel | CollectiveOfferResponseModel
  ) => void
  toggleSelectAllCheckboxes: () => void
  urlSearchFilters: SearchFiltersParams
  isAtLeastOneOfferChecked: boolean
  isRestrictedAsAdmin?: boolean
}

export const Offers = ({
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
  audience,
  isAtLeastOneOfferChecked,
  isRestrictedAsAdmin = false,
}: OffersProps) => {
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
    <div aria-busy={isLoading} aria-live="polite" className="section">
      {isLoading ? (
        <Spinner />
      ) : (
        <>
          {offersCount > MAX_OFFERS_TO_DISPLAY && (
            <Banner type="notification-info">
              L’affichage est limité à 500 offres. Modifiez les filtres pour
              affiner votre recherche.
            </Banner>
          )}
          {hasOffers && (
            <div className={styles['offers-count']}>
              {`${getOffersCountToDisplay(offersCount)} ${
                offersCount <= 1 ? 'offre' : 'offres'
              }`}
            </div>
          )}
          {hasOffers && (
            <>
              <div className={styles['select-all-container']}>
                <BaseCheckbox
                  checked={areAllOffersSelected}
                  partialCheck={
                    !areAllOffersSelected && isAtLeastOneOfferChecked
                  }
                  disabled={isRestrictedAsAdmin}
                  onChange={toggleSelectAllCheckboxes}
                  label={
                    areAllOffersSelected
                      ? 'Tout désélectionner'
                      : 'Tout sélectionner'
                  }
                />
              </div>
              <table>
                <OffersTableHead audience={audience} />
                <OffersTableBody
                  offers={currentPageOffersSubset}
                  selectOffer={setSelectedOffer}
                  selectedOffers={selectedOffers}
                  audience={audience}
                  urlSearchFilters={urlSearchFilters}
                />
              </table>
            </>
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
