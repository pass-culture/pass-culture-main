import React, { useCallback } from 'react'
import { useSelector } from 'react-redux'

import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { MAX_OFFERS_TO_DISPLAY } from 'core/Offers/constants'
import { Offer, SearchFiltersParams } from 'core/Offers/types'
import { hasSearchFilters, isOfferDisabled } from 'core/Offers/utils'
import { Audience } from 'core/shared'
import { getOffersCountToDisplay } from 'pages/Offers/domain/getOffersCountToDisplay'
import NoResults from 'screens/Offers/NoResults'
import { searchFiltersSelector } from 'store/offers/selectors'
import { Banner } from 'ui-kit'
import { BaseCheckbox } from 'ui-kit/form/shared'
import { Pagination } from 'ui-kit/Pagination'
import Spinner from 'ui-kit/Spinner/Spinner'

import styles from './Offers.module.scss'
import OffersTableBody from './OffersTableBody/OffersTableBody'
import OffersTableHead from './OffersTableHead/OffersTableHead'

type OffersProps = {
  applyFilters: () => void
  applyUrlFiltersAndRedirect: (
    filters: SearchFiltersParams,
    isRefreshing: boolean
  ) => void
  areAllOffersSelected: boolean
  audience: Audience
  currentPageNumber: number
  currentPageOffersSubset: Offer[]
  currentUser: { isAdmin: boolean }
  hasOffers: boolean
  isLoading: boolean
  offersCount: number
  pageCount: number
  resetFilters: () => void
  searchFilters: SearchFiltersParams
  selectedOfferIds: string[]
  setSearchFilters: React.Dispatch<React.SetStateAction<SearchFiltersParams>>
  setSelectedOfferIds: React.Dispatch<React.SetStateAction<string[]>>
  toggleSelectAllCheckboxes: () => void
  urlSearchFilters: SearchFiltersParams
  refreshOffers: () => void
  isAtLeastOneOfferChecked: boolean
}

const Offers = ({
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
  refreshOffers,
  isAtLeastOneOfferChecked,
}: OffersProps) => {
  const isAdminForbidden = useCallback(
    (searchFilters: SearchFiltersParams) => {
      return (
        currentUser.isAdmin &&
        !hasSearchFilters(searchFilters, ['venueId', 'offererId'])
      )
    },
    [currentUser.isAdmin]
  )

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

  const selectOffer = useCallback(
    (offerId: number, selected: boolean, isTemplate: boolean) => {
      setSelectedOfferIds((currentSelectedIds) => {
        const newSelectedOfferIds = [...currentSelectedIds]
        const id = computeURLCollectiveOfferId(offerId, isTemplate)
        if (selected) {
          newSelectedOfferIds.push(id)
        } else {
          const offerIdIndex = newSelectedOfferIds.indexOf(id)
          newSelectedOfferIds.splice(offerIdIndex, 1)
        }
        return newSelectedOfferIds
      })
    },
    [setSelectedOfferIds]
  )

  function selectAllOffers() {
    setSelectedOfferIds(
      areAllOffersSelected
        ? []
        : currentPageOffersSubset
            .filter((offer) => !isOfferDisabled(offer.status))
            .map((offer) => offer.id.toString())
    )

    toggleSelectAllCheckboxes()
  }

  const savedSearchFilters = useSelector(searchFiltersSelector)

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

          <div className={styles['select-all-container']}>
            <BaseCheckbox
              checked={areAllOffersSelected || isAtLeastOneOfferChecked}
              partialCheck={!areAllOffersSelected && isAtLeastOneOfferChecked}
              disabled={isAdminForbidden(savedSearchFilters) || !hasOffers}
              onChange={selectAllOffers}
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
              selectAllOffers={selectAllOffers}
              updateStatusFilter={updateStatusFilter}
              audience={audience}
              isAtLeastOneOfferChecked={isAtLeastOneOfferChecked}
            />
            <OffersTableBody
              areAllOffersSelected={areAllOffersSelected}
              offers={currentPageOffersSubset}
              selectOffer={selectOffer}
              selectedOfferIds={selectedOfferIds}
              audience={audience}
              refreshOffers={refreshOffers}
            />
          </table>

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

export default Offers
