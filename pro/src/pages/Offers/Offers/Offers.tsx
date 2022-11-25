import React, { useCallback } from 'react'

import { OfferStatus } from 'apiClient/v1'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { MAX_OFFERS_TO_DISPLAY } from 'core/Offers/constants'
import { Offer, TSearchFilters } from 'core/Offers/types'
import { hasSearchFilters, isOfferDisabled } from 'core/Offers/utils'
import { Audience } from 'core/shared'
import { getOffersCountToDisplay } from 'pages/Offers/domain/getOffersCountToDisplay'
import NoResults from 'screens/Offers/NoResults'
import { Banner } from 'ui-kit'
import Icon from 'ui-kit/Icon/Icon'
import Spinner from 'ui-kit/Spinner/Spinner'

import OffersTableBody from './OffersTableBody/OffersTableBody'
import OffersTableHead from './OffersTableHead/OffersTableHead'

type OffersProps = {
  applyFilters: () => void
  applyUrlFiltersAndRedirect: (
    filters: TSearchFilters,
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
  pageCount?: number
  resetFilters: () => void
  searchFilters: TSearchFilters
  selectedOfferIds: string[]
  setSearchFilters: React.Dispatch<React.SetStateAction<TSearchFilters>>
  setSelectedOfferIds: React.Dispatch<React.SetStateAction<string[]>>
  toggleSelectAllCheckboxes: () => void
  urlSearchFilters: TSearchFilters
  refreshOffers: () => void
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
}: OffersProps) => {
  const isAdminForbidden = useCallback(
    (searchFilters: TSearchFilters) => {
      return (
        currentUser.isAdmin &&
        !hasSearchFilters(searchFilters, ['venueId', 'offererId'])
      )
    },
    [currentUser.isAdmin]
  )

  const updateStatusFilter = useCallback(
    (selectedStatus: OfferStatus | 'all') => {
      setSearchFilters((currentSearchFilters: TSearchFilters) => ({
        ...currentSearchFilters,
        status: selectedStatus,
      }))
    },
    [setSearchFilters]
  )

  const onPreviousPageClick = useCallback(() => {
    const newPageNumber = currentPageNumber - 1
    applyUrlFiltersAndRedirect(
      { ...urlSearchFilters, ...{ page: newPageNumber } },
      false
    )
  }, [currentPageNumber, applyUrlFiltersAndRedirect, urlSearchFilters])

  const onNextPageClick = useCallback(() => {
    const newPageNumber = currentPageNumber + 1
    applyUrlFiltersAndRedirect(
      { ...urlSearchFilters, ...{ page: newPageNumber } },
      false
    )
  }, [currentPageNumber, applyUrlFiltersAndRedirect, urlSearchFilters])

  const selectOffer = useCallback(
    (offerId: string, selected: boolean, isTemplate: boolean) => {
      setSelectedOfferIds(currentSelectedIds => {
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
            .filter(offer => !isOfferDisabled(offer.status))
            .map(offer => offer.id)
    )

    toggleSelectAllCheckboxes()
  }

  const isLastPage = currentPageNumber === pageCount

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
            <div className="offers-count">
              {`${getOffersCountToDisplay(offersCount)} ${
                offersCount <= 1 ? 'offre' : 'offres'
              }`}
            </div>
          )}
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
            <div className="pagination">
              <button
                disabled={currentPageNumber === 1}
                onClick={onPreviousPageClick}
                type="button"
              >
                <Icon alt="page précédente" svg="ico-left-arrow" />
              </button>
              <span>{`Page ${currentPageNumber}/${pageCount}`}</span>
              <button
                disabled={isLastPage}
                onClick={onNextPageClick}
                type="button"
              >
                <Icon alt="page suivante" svg="ico-right-arrow" />
              </button>
            </div>
          )}
          {!hasOffers && hasSearchFilters(urlSearchFilters) && (
            <NoResults audience={audience} resetFilters={resetFilters} />
          )}
        </>
      )}
    </div>
  )
}

export default Offers
