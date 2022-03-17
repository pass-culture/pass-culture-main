import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'
import { useHistory } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import Spinner from 'components/layout/Spinner'
import { getOffersCountToDisplay } from 'components/pages/Offers/domain/getOffersCountToDisplay'
import { isOfferDisabled } from 'components/pages/Offers/domain/isOfferDisabled'
import {
  DEFAULT_SEARCH_FILTERS,
  MAX_OFFERS_TO_DISPLAY,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
} from 'core/Offers/constants'
import { useQuerySearchFilters } from 'core/Offers/hooks'
import * as pcapi from 'repository/pcapi/pcapi'
import { savePageNumber, saveSearchFilters } from 'store/offers/actions'
import { Banner } from 'ui-kit'

import { computeOffersUrl } from '../utils/computeOffersUrl'

import NoResults from './NoResults/NoResults'
import OffersTableBody from './OffersTableBody/OffersTableBody'
import OffersTableHead from './OffersTableHead/OffersTableHead'
import SearchFilters from './SearchFilters/SearchFilters'

const Offers = ({
  currentUser,
  getOfferer,
  areAllOffersSelected,
  currentPageNumber,
  currentPageOffersSubset,
  hasOffers,
  hasSearchFilters,
  isLoading,
  isRefreshingOffers,
  offerer,
  offersCount,
  pageCount,
  refreshOffers,
  resetFilters,
  searchFilters,
  selectedOfferIds,
  setCurrentPageNumber,
  setIsLoading,
  setIsRefreshingOffers,
  setOfferer,
  setOffers,
  setOffersCount,
  setPageCount,
  setSearchFilters,
  setSelectedOfferIds,
  toggleSelectAllCheckboxes,
  urlSearchFilters,
}) => {
  const dispatch = useDispatch()
  const history = useHistory()
  const [urlPageNumber] = useQuerySearchFilters()

  useEffect(() => {
    setCurrentPageNumber(urlPageNumber)
    dispatch(
      saveSearchFilters({
        nameOrIsbn:
          urlSearchFilters.nameOrIsbn || DEFAULT_SEARCH_FILTERS.nameOrIsbn,
        offererId:
          urlSearchFilters.offererId || DEFAULT_SEARCH_FILTERS.offererId,
        venueId: urlSearchFilters.venueId || DEFAULT_SEARCH_FILTERS.venueId,
        categoryId:
          urlSearchFilters.categoryId || DEFAULT_SEARCH_FILTERS.categoryId,
        status: urlSearchFilters.status
          ? urlSearchFilters.status
          : DEFAULT_SEARCH_FILTERS.status,
        creationMode: urlSearchFilters.creationMode
          ? urlSearchFilters.creationMode
          : DEFAULT_SEARCH_FILTERS.creationMode,
        periodBeginningDate:
          urlSearchFilters.periodBeginningDate ||
          DEFAULT_SEARCH_FILTERS.periodBeginningDate,
        periodEndingDate:
          urlSearchFilters.periodEndingDate ||
          DEFAULT_SEARCH_FILTERS.periodEndingDate,
      })
    )
    dispatch(savePageNumber(urlPageNumber))
  }, [dispatch, urlPageNumber, urlSearchFilters, setCurrentPageNumber])
  const [isStatusFiltersVisible, setIsStatusFiltersVisible] = useState(false)

  const applyUrlFiltersAndRedirect = useCallback(
    (filters, isRefreshing = true) => {
      setIsRefreshingOffers(isRefreshing)
      const newUrl = computeOffersUrl(filters, filters.page)

      history.push(newUrl)
    },
    [history, setIsRefreshingOffers]
  )

  useEffect(() => {
    if (
      urlSearchFilters.offererId &&
      urlSearchFilters.offererId !== DEFAULT_SEARCH_FILTERS.offererId
    ) {
      getOfferer(urlSearchFilters.offererId).then(offerer =>
        setOfferer(offerer)
      )
    }
  }, [getOfferer, urlSearchFilters.offererId, setOfferer])

  useEffect(() => {
    if (currentUser.isAdmin) {
      const isVenueFilterSelected =
        searchFilters.venueId !== DEFAULT_SEARCH_FILTERS.venueId
      const isOffererFilterApplied =
        urlSearchFilters.offererId !== DEFAULT_SEARCH_FILTERS.offererId
      const isFilterByVenueOrOfferer =
        isVenueFilterSelected || isOffererFilterApplied

      if (!isFilterByVenueOrOfferer) {
        setSearchFilters(currentSearchFilters => ({
          ...currentSearchFilters,
          status: DEFAULT_SEARCH_FILTERS.status,
        }))
      }
    }
  }, [
    currentUser.isAdmin,
    urlSearchFilters.offererId,
    searchFilters.venueId,
    setSearchFilters,
  ])

  const loadAndUpdateOffers = useCallback(
    filters => {
      const apiFilters = {
        ...DEFAULT_SEARCH_FILTERS,
        ...filters,
      }
      pcapi
        .loadFilteredOffers(apiFilters)
        .then(offers => {
          const offersCount = offers.length
          setIsLoading(false)
          setOffersCount(offersCount)
          const pageCount = Math.ceil(offersCount / NUMBER_OF_OFFERS_PER_PAGE)
          const cappedPageCount = Math.min(pageCount, MAX_TOTAL_PAGES)
          setPageCount(cappedPageCount)
          setOffers(offers)
        })
        .catch(() => setIsLoading(false))
    },
    [setIsLoading, setOffersCount, setPageCount, setOffers]
  )

  const hasDifferentFiltersFromLastSearch = useCallback(
    (searchFilters, filterNames = Object.keys(searchFilters)) => {
      const lastSearchFilters = {
        ...DEFAULT_SEARCH_FILTERS,
        ...urlSearchFilters,
      }
      return filterNames
        .map(
          filterName =>
            searchFilters[filterName] !== lastSearchFilters[filterName]
        )
        .includes(true)
    },
    [urlSearchFilters]
  )
  const applyFilters = useCallback(() => {
    setIsLoading(true)
    setIsStatusFiltersVisible(false)

    if (!hasDifferentFiltersFromLastSearch(searchFilters)) {
      refreshOffers()
    }
    applyUrlFiltersAndRedirect(searchFilters)
  }, [
    hasDifferentFiltersFromLastSearch,
    refreshOffers,
    searchFilters,
    applyUrlFiltersAndRedirect,
    setIsLoading,
  ])

  useEffect(() => {
    if (isRefreshingOffers) {
      setSearchFilters(urlSearchFilters)
      loadAndUpdateOffers(urlSearchFilters)
    }
  }, [
    isRefreshingOffers,
    loadAndUpdateOffers,
    setSearchFilters,
    urlSearchFilters,
  ])

  const removeOfferer = useCallback(() => {
    setIsLoading(true)
    setOfferer(null)
    const updatedFilters = {
      ...searchFilters,
      offererId: DEFAULT_SEARCH_FILTERS.offererId,
    }
    if (
      searchFilters.venueId === DEFAULT_SEARCH_FILTERS.venueId &&
      searchFilters.status !== DEFAULT_SEARCH_FILTERS.status
    ) {
      updatedFilters.status = DEFAULT_SEARCH_FILTERS.status
    }
    applyUrlFiltersAndRedirect(updatedFilters)
  }, [applyUrlFiltersAndRedirect, searchFilters, setIsLoading, setOfferer])

  const isAdminForbidden = useCallback(
    searchFilters => {
      return (
        currentUser.isAdmin &&
        !hasSearchFilters(searchFilters, ['venueId', 'offererId'])
      )
    },
    [currentUser.isAdmin, hasSearchFilters]
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
    (offerId, selected) => {
      setSelectedOfferIds(currentSelectedIds => {
        let newSelectedOfferIds = [...currentSelectedIds]
        if (selected) {
          newSelectedOfferIds.push(offerId)
        } else {
          const offerIdIndex = newSelectedOfferIds.indexOf(offerId)
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
    <>
      <SearchFilters
        applyFilters={applyFilters}
        offerer={offerer}
        removeOfferer={removeOfferer}
        selectedFilters={searchFilters}
        setSearchFilters={setSearchFilters}
      />

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
                isStatusFiltersVisible={isStatusFiltersVisible}
                selectAllOffers={selectAllOffers}
                setIsStatusFiltersVisible={setIsStatusFiltersVisible}
                updateStatusFilter={updateStatusFilter}
              />
              <OffersTableBody
                areAllOffersSelected={areAllOffersSelected}
                offers={currentPageOffersSubset}
                selectOffer={selectOffer}
                selectedOfferIds={selectedOfferIds}
              />
            </table>
            {hasOffers && (
              <div className="pagination">
                <button
                  disabled={currentPageNumber === 1}
                  onClick={onPreviousPageClick}
                  type="button"
                >
                  <Icon alt="Aller à la page précédente" svg="ico-left-arrow" />
                </button>
                <span>{`Page ${currentPageNumber}/${pageCount}`}</span>
                <button
                  disabled={isLastPage}
                  onClick={onNextPageClick}
                  type="button"
                >
                  <Icon alt="Aller à la page suivante" svg="ico-right-arrow" />
                </button>
              </div>
            )}
            {!hasOffers && hasSearchFilters(urlSearchFilters) && (
              <NoResults resetFilters={resetFilters} />
            )}
          </>
        )}
      </div>
    </>
  )
}

Offers.defaultProps = {
  offerer: null,
  pageCount: null,
}

Offers.propTypes = {
  areAllOffersSelected: PropTypes.bool.isRequired,
  currentPageNumber: PropTypes.number.isRequired,
  currentPageOffersSubset: PropTypes.shape().isRequired,
  currentUser: PropTypes.shape().isRequired,
  getOfferer: PropTypes.func.isRequired,
  hasOffers: PropTypes.bool.isRequired,
  hasSearchFilters: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
  isRefreshingOffers: PropTypes.bool.isRequired,
  offerer: PropTypes.shape(),
  offersCount: PropTypes.number.isRequired,
  pageCount: PropTypes.number,
  refreshOffers: PropTypes.func.isRequired,
  resetFilters: PropTypes.func.isRequired,
  searchFilters: PropTypes.shape().isRequired,
  selectedOfferIds: PropTypes.shape.isRequired,
  setCurrentPageNumber: PropTypes.func.isRequired,
  setIsLoading: PropTypes.func.isRequired,
  setIsRefreshingOffers: PropTypes.func.isRequired,
  setOfferer: PropTypes.func.isRequired,
  setOffers: PropTypes.func.isRequired,
  setOffersCount: PropTypes.func.isRequired,
  setPageCount: PropTypes.func.isRequired,
  setSearchFilters: PropTypes.func.isRequired,
  setSelectedOfferIds: PropTypes.func.isRequired,
  toggleSelectAllCheckboxes: PropTypes.func.isRequired,
  urlSearchFilters: PropTypes.shape().isRequired,
}

export default Offers
