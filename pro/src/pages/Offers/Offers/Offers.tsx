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
  applyFilters: () => void
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
  searchFilters: SearchFiltersParams
  selectedOfferIds: number[]
  setSearchFilters: React.Dispatch<React.SetStateAction<SearchFiltersParams>>
  setSelectedOfferIds: React.Dispatch<React.SetStateAction<number[]>>
  toggleSelectAllCheckboxes: () => void
  urlSearchFilters: SearchFiltersParams
  isAtLeastOneOfferChecked: boolean
}

export const Offers = ({
  applyFilters,
  currentUser,
  areAllOffersSelected,
  currentPageNumber,
  currentPageOffersSubset,
  hasOffers,
  isLoading,
  offersCount,
  pageCount,
  resetFilters,
  searchFilters,
  selectedOfferIds,
  applyUrlFiltersAndRedirect,
  setSearchFilters,
  setSelectedOfferIds,
  toggleSelectAllCheckboxes,
  urlSearchFilters,
  audience,
  isAtLeastOneOfferChecked,
}: OffersProps) => {
  const isAdminForbidden = (searchFilters: Partial<SearchFiltersParams>) => {
    return (
      currentUser.isAdmin &&
      !hasSearchFilters(searchFilters, ['venueId', 'offererId'])
    )
  }

  const updateStatusFilter = (
    selectedStatus: SearchFiltersParams['status']
  ) => {
    setSearchFilters((currentSearchFilters) => ({
      ...currentSearchFilters,
      status: selectedStatus,
    }))
  }

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

  function selectOffer(offerId: number, isAlreadyChecked: boolean) {
    setSelectedOfferIds((currentSelectedIds) => {
      const newSelectedOfferIds = [...currentSelectedIds]
      if (isAlreadyChecked) {
        newSelectedOfferIds.push(offerId)
      } else {
        const offerIdIndex = newSelectedOfferIds.indexOf(offerId)
        newSelectedOfferIds.splice(offerIdIndex, 1)
      }
      return newSelectedOfferIds
    })
  }

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
                  disabled={isAdminForbidden(searchFilters)}
                  onChange={toggleSelectAllCheckboxes}
                  label={
                    areAllOffersSelected
                      ? 'Tout désélectionner'
                      : 'Tout sélectionner'
                  }
                />
              </div>
              <table>
                <OffersTableHead
                  applyFilters={applyFilters}
                  areAllOffersSelected={areAllOffersSelected}
                  areOffersPresent={hasOffers}
                  filters={searchFilters}
                  isAdminForbidden={isAdminForbidden}
                  updateStatusFilter={updateStatusFilter}
                  audience={audience}
                  isAtLeastOneOfferChecked={isAtLeastOneOfferChecked}
                />
                <OffersTableBody
                  offers={currentPageOffersSubset}
                  selectOffer={selectOffer}
                  selectedOfferIds={selectedOfferIds}
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
