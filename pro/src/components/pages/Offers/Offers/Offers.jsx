import React, { useCallback } from 'react'

import { Banner } from 'ui-kit'
import Icon from 'components/layout/Icon'
import { MAX_OFFERS_TO_DISPLAY } from 'core/Offers/constants'
import NoResults from 'screens/Offers/NoResults'
import OffersTableBody from './OffersTableBody/OffersTableBody'
import OffersTableHead from './OffersTableHead/OffersTableHead'
import PropTypes from 'prop-types'
import Spinner from 'components/layout/Spinner'
import { getOffersCountToDisplay } from 'components/pages/Offers/domain/getOffersCountToDisplay'
import { hasSearchFilters } from 'core/Offers/utils'
import { isOfferDisabled } from 'components/pages/Offers/domain/isOfferDisabled'
import useActiveFeature from 'components/hooks/useActiveFeature'

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
}) => {
  const isAdminForbidden = useCallback(
    searchFilters => {
      return (
        currentUser.isAdmin &&
        !hasSearchFilters(searchFilters, ['venueId', 'offererId'])
      )
    },
    [currentUser.isAdmin]
  )
  const isNewModelEnabled = useActiveFeature('ENABLE_NEW_COLLECTIVE_MODEL')
  const enableIndividualAndCollectiveSeparation = useActiveFeature(
    'ENABLE_INDIVIDUAL_AND_COLLECTIVE_OFFER_SEPARATION'
  )

  const updateStatusFilter = useCallback(
    selectedStatus => {
      setSearchFilters(currentSearchFilters => ({
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
    (offerId, selected, isTemplate) => {
      setSelectedOfferIds(currentSelectedIds => {
        let newSelectedOfferIds = [...currentSelectedIds]
        const id = isNewModelEnabled
          ? `${isTemplate ? 'T-' : ''}${offerId}`
          : offerId
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
            />
            <OffersTableBody
              areAllOffersSelected={areAllOffersSelected}
              offers={currentPageOffersSubset}
              selectOffer={selectOffer}
              selectedOfferIds={selectedOfferIds}
              isNewModelEnabled={isNewModelEnabled}
              enableIndividualAndCollectiveSeparation={
                enableIndividualAndCollectiveSeparation
              }
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

Offers.defaultProps = {
  pageCount: null,
}

Offers.propTypes = {
  applyFilters: PropTypes.func.isRequired,
  applyUrlFiltersAndRedirect: PropTypes.func.isRequired,
  areAllOffersSelected: PropTypes.bool.isRequired,
  audience: PropTypes.string.isRequired,
  currentPageNumber: PropTypes.number.isRequired,
  currentPageOffersSubset: PropTypes.shape().isRequired,
  currentUser: PropTypes.shape().isRequired,
  hasOffers: PropTypes.bool.isRequired,
  isLoading: PropTypes.bool.isRequired,
  offersCount: PropTypes.number.isRequired,
  pageCount: PropTypes.number,
  resetFilters: PropTypes.func.isRequired,
  searchFilters: PropTypes.shape().isRequired,
  selectedOfferIds: PropTypes.shape.isRequired,
  setSearchFilters: PropTypes.func.isRequired,
  setSelectedOfferIds: PropTypes.func.isRequired,
  toggleSelectAllCheckboxes: PropTypes.func.isRequired,
  urlSearchFilters: PropTypes.shape().isRequired,
}

export default Offers
